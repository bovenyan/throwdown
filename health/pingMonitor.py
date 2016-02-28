import subprocess
import sys
import db_conn 
from time import sleep

not_reachable_thres = 10
latency_avg_times = 5  # update latency every after 5 sec
loss_rate_agg_times = 15
db = db_conn.db_api()

class icmp_monitor():
    def __init__(self, ip, lsp):
        self.ip = ip
        self.lsp = lsp
        self.last_seq = 0

        self.count_down = latency_avg_times
        self.loss_count_down = loss_rate_agg_times
        self.reachability_count_down = latency_avg_times * 3

        # for latency
        self.agg_latency = 0
        self.reachable_msg = 0
        # for loss
        self.packet_loss = 0
        self.packet_recv = 0

        self.loss_rate = 0.0
        self.latency = 0.0

        self.process = None

    def start(self):
        self.process = subprocess.Popen("ping " + self.ip, shell=True, stdout=subprocess.PIPE)

        for icmp_msg in iter(lambda: self.process.stdout.readline(), ''):
            # parse the msg
            # print icmp_msg
            self.parse_msg(icmp_msg)

    def parse_msg(self, icmp_msg):
        icmp_ele = icmp_msg.split(" ")
        if (len(icmp_ele) == 8):  # correct mess
            if "icmp_seq" in icmp_ele[4]:
                cur_seq = int(icmp_ele[4].split("=")[1])
                loss = cur_seq - self.last_seq - 1;
                self.last_seq = cur_seq

                self.packet_loss = self.packet_loss + loss
                self.packet_recv = self.packet_recv + 1;
                self.reachable_msg = self.reachable_msg + 1
                self.loss_count_down = self.loss_count_down -1

                if (self.loss_count_down == 0):
                    self.loss_count_down = loss_rate_agg_times
                    if (self.packet_recv == 0 and self.packet_loss == 0):
                        self.loss_rate = 100.0
                    else:
                        self.loss_rate = float(self.packet_loss)/(self.packet_recv + self.packet_loss)

                    print "loss: " + str(self.loss_rate)

            if "time" in icmp_ele[6]:
                latency = float(icmp_ele[6].split("=")[1])
                self.agg_latency = self.agg_latency + latency
                self.count_down = self.count_down - 1;
                self.reachability_count_down = latency_avg_times * 3

                if (self.count_down == 0):
                    self.count_down = latency_avg_times
                    if (self.reachable_msg != 0):
                        self.latency = self.agg_latency/self.reachable_msg
                    else:
                        self.latency = 10000
                    
                    print "avg latency: " + str(self.latency)
                    # TODO: database
                    db.update_health(self.lsp, self.latency, self.loss_rate)
                    self.reachable_msg = 0
                    self.agg_latency = 0

        elif (len(icmp_ele) == 6):  # not reachable
            self.packet_recv = self.packet_recv + 1
            self.reachability_count_down = self.reachability_count_down - 1

            if (self.reachability_count_down == 0):
                print "not reachable"
                self.latency = 20000
                self.loss_rate = 100
                # TODO update database
                db.update_health(self.lsp, self.latency, self.loss_rate)
                self.reachability_count_down = latency_avg_times * 3

        else: # ignore
            print "received unexpected message"
            pass
    
    def stop(self):
        self.process.terminate()

def monitor_process_callback(ip, lsp):
    sleep(10)
    print "end to end monitoring start on lsp: " + str(lsp) + " ip: " + ip
    monitor = icmp_monitor(ip, lsp)
    monitor.start()

