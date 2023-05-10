import pickle
import time
from os import system
import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('additionalData/Wild_Flower\\mel.dat', 'rb') as f:
        s = pickle.load(f)


    #system('start D:\\Document\\GitHub\\vocalMaximum\\temp\\야생화\\vocals.wav')

    plt.plot(s)
    plt.show()

    #stt=time.time()
    #while True:
    #    print(s[int((time.time()-stt)*22050/512)])