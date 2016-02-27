# generate multiple iperf flows....

from subprocess import Popen

class iperf_app():
    def __init__(self, port, is_server=False, ip="192.168.5.1"):
        self.port = port
        self.role = is_server
        self.ip = ip

    def start(self):
        # server
        if self.role:

        else:   # register flow


    def stop(self):
