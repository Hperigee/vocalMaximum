import pickle
from fileinput import input_file
from queue import Queue
from spleeter.separator import Separator
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

global to_process
to_process= Queue()

def enqueue_files(filelist):
    for file in filelist:
        print(file, "input success")
        to_process.put(file)
    return
def process(filelist,spl):
    enqueue_files(filelist)
    A=[]
    while not to_process.empty():
        file = to_process.get()
        print(file, "start process")
        res = input_file(file,spl)
        print("finish process")
        A.append(res)
    return A

if __name__=="__main__":
    GLOBAL_SPLITTER = Separator('spleeter:2stems', stft_backend='tensorflow', multiprocess=False)

    folder_path = 'Defaults'
    datas = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3')]
    data = process(datas,GLOBAL_SPLITTER)

    data.sort(key=lambda x: x.name)

    with open(f'./Datas/Defaultlist.dat', 'wb') as file:
        pickle.dump(data, file)
        del data
