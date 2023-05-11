from queue import Queue
import time
global STOP
STOP = False
def asdf(queue: Queue):
    i = 0
    while not STOP:
        queue.put([f'{i}saf',f'{i*10}'])
        time.sleep(0.001)
        i+=1
    print("loop finished")
