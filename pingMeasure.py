from health.pingMonitor import *
from multiprocessing import Process

measure_info = []
measure_info.append(["192.168.6.2", "192.168.6.1", 6])
measure_info.append(["192.168.7.2", "192.168.7.1", 7])
measure_info.append(["192.168.8.2", "192.168.8.1", 8])
measure_info.append(["192.168.9.2", "192.168.9.1", 9])

if __name__ == "__main__":
    process = [None, None, None, None]
    for mLsp in range(4):
        process[mLsp] = Process(target=monitor_process_callback,
                                args=(measure_info[mLsp][1],
                                mLsp))
        process[mLsp].start()

    for mLsp in range(4):
        process[mLsp].join()
