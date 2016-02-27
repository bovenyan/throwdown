from multiprocessing import Process
from pingMonitor import *

if __name__ == "__main__":
    lsp0_monitor = Process(target=monitor_process_callback, args=("192.168.1.1", 0))
    lsp1_monitor = Process(target=monitor_process_callback, args=("192.168.2.1", 1))

    lsp0_monitor.start()
    lsp1_monitor.start()

    lsp0_monitor.join()
    lsp1_monitor.join()
