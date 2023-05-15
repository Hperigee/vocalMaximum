from queue import Queue
import time
global STOP
STOP = False
def asdf(queue: Queue):
    i = 0
    while not STOP:
        queue.put([f'더 높게',f'더 세게'])
        time.sleep(0.001)
        i+=1
    print("loop finished")
