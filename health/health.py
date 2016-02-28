from db_conn import db_api

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

    for lsp in range(4):
        metrix_rev = db.get_lsp_metrix(lsp+4)
        if (metrix_rev[2] < metrix[lsp][2]):
            metrix[lsp][2] = metrix_rev[2]

    if (max_bw == 0 or max_latency == 0):
        print "we have an error in metrix"

    for lsp in range(4):
        bw_norm[lsp] = metrix[lsp][2]/max_bw
        latency_norm[lsp] = metrix[lsp][0]/max_latency

    return bw_norm, latency_norm, loss_norm

def cal_healthest(qos=0):
    bw, latency, loss = fetch_metrix()

    score = [0.0, 0.0, 0.0, 0.0]
    highest_score = 0.0
    winner = 1

    if (qos == 0):  # default
        for lsp in range(4):
            score[lsp] = bw[lsp] + (1-latency[lsp]) + (1-loss[lsp])
            if (score[lsp] > highest_score):
                winner = lsp
                highest_score = score[lsp]

        return winner 

    if (qos == 1):  # tcp 
        for lsp in range(4):
            score[lsp] = bw[lsp] + (1-loss[lsp])
            if (score[lsp] > highest_score):
                winner = lsp
                highest_score = score[lsp]
        return winner 

    if (qos == 2):  # udp
        for lsp in range(4):
            score[lsp] = bw[lsp] + (1-latency[lsp])
            if (score[lsp] > highest_score):
                winner = lsp
                highest_score = score[lsp]
        return winner 

if __name__ == "__main__":
    print cal_healthest(0)
    print cal_healthest(1)
    print cal_healthest(2)
