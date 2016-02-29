from db_conn import db_api
import random
import time
from datetime import datetime, timedelta
db = db_api()

def fetch_metrix():
    max_bw = float(0)
    max_latency = float(0)
    max_loss = float(0)

    bw_norm = [0, 0, 0, 0]
    latency_norm = [0, 0, 0, 0]
    loss_norm = [0, 0, 0, 0]

    metrix = [None, None, None, None]

    for lsp in range(4):
        metrix[lsp] = list(db.get_lsp_metrix(lsp))

        if (metrix[lsp][2] > max_bw):
            max_bw = metrix[lsp][2]
        if (metrix[lsp][0] > max_latency):
            max_latency = metrix[lsp][0]
        loss_norm[lsp] = metrix[lsp][1]

    last_update = metrix[0][5]

    for lsp in range(4):
        metrix_rev = db.get_lsp_metrix(lsp+4)
        if (metrix_rev[2] < metrix[lsp][2]):
            metrix[lsp][2] = metrix_rev[2]

    if (max_bw == 0 or max_latency == 0):
        print "we have an error in metrix"

    for lsp in range(4):
        bw_norm[lsp] = metrix[lsp][2]/max_bw
        latency_norm[lsp] = metrix[lsp][0]/max_latency

    return bw_norm, latency_norm, loss_norm, last_update

def cal_healthest(qos=0, eastOriented=False):
    bw, latency, loss, last_update = fetch_metrix()

    score = [0.0, 0.0, 0.0, 0.0]
    highest_score = 0.0
    winner = 1

    if (qos == 0):  # greedy
        for lsp in range(4):
            score[lsp] = bw[lsp] + (1-latency[lsp]) + (1-loss[lsp])
            if (score[lsp] > highest_score):
                winner = lsp
                highest_score = score[lsp]

        return winner

    if (qos == 1):  # proportionaly
        sum_bw = sum(bw)
        for lsp in range(4):
            bw[lsp] = bw[lsp]/sum_bw
        bw = [0] + bw
        randf = random.random()
        # print bw, randf
        for lsp in range(4):
            bw[lsp+1] = bw[lsp] + bw[lsp+1]
            if randf >= bw[lsp] and randf < bw[lsp+1]:
                return lsp
        return random.randint(0,3)

    if (qos == 2):  # greedy but with trust of Bw
        trust_to_ping = (datetime.now() - last_update).second/30
        if trust_to_ping < 0:
            trust_to_ping = 0
        if trust_to_ping > 1:
            trust_to_ping = 1

        for lsp in range(4):
            score[lsp] = bw[lsp] * (1-trust_to_ping) + \
                         + (1-latency[lsp]) * trust_to_ping

    if (qos == 3):  # proportionaly but aware of other flows
        nouse = list(set(db.unavailable_lsps(2, eastOriented)))
        nouse.sort()

        use = []

        if len(nouse) == 4:
            use = range(4)
        else:
            for i in range(4):
                if not (i in nouse):
                    use.append(i)
                else:
                    del bw[i]
        bw = [0] + bw
        randf = random.random() * sum(bw)

        for i in range(len(use)):
            bw[i+1] = bw[i+1] + bw[i]
            if randf > bw[i] and randf < bw[i+1]:
                return use[i]

        return random.choice(use)

if __name__ == "__main__":
    print cal_healthest(0)
    print cal_healthest(1)
    print cal_healthest(2)
