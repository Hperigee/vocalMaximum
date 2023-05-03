import pickle
import time
from os import system

if __name__ == '__main__':
    with open('additionalData/Wild_Flower\\mel.dat', 'rb') as f:
        s = pickle.load(f)


    system('start C:\\Users\\829ho\\Documents\\GitHub\\vocalMaximum\\temp\\Wild_Flower\\vocals.wav')
    stt = time.time()


    while True:
        print(s[int((time.time()-stt)*22050/512)])