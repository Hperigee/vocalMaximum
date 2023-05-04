import pickle
import time
import numpy as np
from os import system
import matplotlib.pyplot as plt

if __name__ == '__main__':

    S_f_dB = [0, 0, 0, 40, 0, 10, 40, 10, 10, 50, 10, 5, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 4, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    result = [0] * 206

    for i in range(2, 200):
        for j in range(1, len(S_f_dB)):
            result[i] += S_f_dB[j] * np.cos(2 * np.pi * j / i)

    for i in result:
        print(round(i, 3))

    S_f_dB = np.abs(np.fft.fft(S_f_dB))

    print(S_f_dB)