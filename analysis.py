import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time
import copy

def _plt_show(spectrogram_db):
    if __name__ == '__main__':
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        img = librosa.display.specshow(spectrogram_db, x_axis='time', y_axis='hz', ax=ax)
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.xlabel('time')
        plt.ylabel('freq')

        plt.show()

'''
def _score_func(L):
    n=len(L)
    sum=0
    k=1
    for db in L:
       sum+=(10**(int(db/10+8)))/(k**2)
       k+=1
    return sum*(n**2)


def _find_peek(S, frame):  # return list of peek frequency and dB weight

    threshold = 0  # constant

    freq_list = librosa.fft_frequencies()
    scores = [0] * 200
    para_list = []

    for i in range(6, 206):

        for j in range(i, 24 * i + 1, i):
            if j < 1024: para_list += [S[j][frame]]
            else: para_list += [-80.0]
        
        scores[i-6] = _score_func(para_list)
        para_list = []

    mx = max(scores)
    bass_ind = scores.index(mx) + 6

    if mx > threshold and bass_ind: return [[freq_list[bass_ind], S[bass_ind][frame]],
                               [freq_list[2 * bass_ind], S[2 * bass_ind][frame]],
                               [freq_list[3 * bass_ind], S[3 * bass_ind][frame]]]
    return []
    # [] or [[hz, dB], [hz, dB], [hz, dB]]
'''

'''
def _find_peek(S, freq):  # S[ind] = dB, freq = librosa.fft_frequencies()
    result = np.zeros(206)
    n = len(S)
    mx = 0
    ind = 0

    for i in range(6, 206):
        result[i] = np.dot(S, np.cos(np.linspace(0, 2 * np.pi * (n - 1) / i, n)))

        if 750 < result[i - 1] and mx < result[i - 1] and result[i - 2] <= result[i - 1] > result[i]\
                and max(result[i-1] - result[i], result[i-1] - result[i-2]) > 100:
            mx, ind = result[i - 1], i - 1

    import matplotlib.pyplot as plt

    plt.plot(freq[:206], result)
    plt.show()
    
    if ind == 0: return []
    else:
        return [[freq[i], S[i - 1] + S[i] + S[i + 1]] for i in range(ind, 3 * ind + 1, ind)]
'''


def _gpt_peek(S, freq, cos_mat, S_mat):
    result = np.zeros(630)
    #n = len(S)


    #result[6:206] = np.array([np.dot(S, np.cos(np.linspace(0, 6.283184 * (n - 1) / i, n))) for i in range(6, 206)])
    #result[6:206] = np.array([np.dot(S, np.cos(np.linspace(0, 3952.1235 / i, 630))) for i in range(6, 206)])
    #result[6:206] = np.array([np.dot(S, np.cos(np.linspace(0, i, 630))) for i in iz])
    result[18:630] = np.sum(S_mat * cos_mat, axis=1)

    # Vectorize the conditions to identify the peak frequencies
    cond = (600 < result[17:629]) & (result[16:628] <= result[17:629]) & (result[17:629] > result[18:630]) & \
           (np.maximum(result[17:629] - result[18:630], result[17:629] - result[16:628]) > 100)
    idx = np.flatnonzero(cond) + 17

    if len(idx) == 0: return []

    ind3 = idx[np.argmax(result[idx])]  # 3배음의 freq index
    ind1i = ind3 // 3
    ind2i = ind3 * 2 // 3
    ind1p3 = ind3 % 3
    ind2p3 = ind3 * 2 % 3

    return [[freq[ind1i] + ind1p3 * 3.5888673,
             S[ind1i - 1] * (3 - ind1p3) / 3 + S[ind1i] + S[ind1i + 1] + ind1p3 * S[ind1i + 2] / 3],
            [freq[ind2i] + ind2p3 * 3.5888673,
             S[ind2i - 1] * (2 - ind2p3) * 0.5 + S[ind2i] + S[ind2i + 1] + ind2p3 * S[ind2i + 2] * 0.5],
            [freq[ind3], S[ind3 - 1] + S[ind3] + S[ind3 + 1]]]


def _export_melody(vocal_feature):
    L = []  # L[frame] -> hz  or  -1
    for i in vocal_feature:
        if len(i) != 0: L.append(i[1][0])
        else: L.append(-1)
    return L


def _export_strength(vocal_feature):
    L = []  # L[frame] -> strength: 0 ~ 2  or  -1
    for i in vocal_feature:
        if len(i) != 0: L.append((1 * i[1][1] + 2 * i[2][1]) / (i[0][1] + i[1][1] + i[2][1]))
        else: L.append(-1)
    return L


def _denoise(S, threshold):
    S = np.array(S)



def file_analysis(filename):
    delta = time.time()

    song_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    raw_wave, sr = librosa.load(song_directory)

    spectrogram_db = librosa.stft(y=raw_wave)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram_db), ref=np.max)
    # spectrogram_db[level][frame]
    # 1 frame == 512 / sr=22050 sec
    # use librosa.fft_frequencies() to learn
    print("loaded", time.time() - delta)
    freq = librosa.fft_frequencies()
    '''
    freq_list = librosa.fft_frequencies()
    max_ind = 222
    for i in range(len(freq_list)):
        if freq_list[i] > max_hz:
            max_ind = i
            break
    '''
    delta = time.time()

    end = 6 * np.pi * 629

    cos_mat = np.cos(np.array([np.linspace(0, end / i, 630) for i in range(18, 630)]))

    vocal_feature = []
    for frame in range(len(spectrogram_db[0])):
        S = np.ravel(spectrogram_db[0:len(spectrogram_db), frame:frame + 1])[:630] + 80
        S_mat = np.tile(S, (612, 1))
        vocal_feature.append(_gpt_peek(S, freq, cos_mat, S_mat))
    # now vocal_feature has 3 harmonics hz and dB of vocal with format:
    # vocal_feature[frame][1~3rd harmonics] -> [hz, dB sum of near hz]

    print(vocal_feature[10379])
    print(vocal_feature[10200])

    print("processed", time.time() - delta)
    delta = time.time()

    melody = _export_melody(vocal_feature)
    timeline = np.arange(len(melody)) * 512 / 22050

    print("exported", time.time() - delta)

    plt.plot(timeline, melody, 'ro', ms=2)

    plt.show()



    '''
    print(len(melody))
    newmelody=copy.deepcopy(melody)
    for i in range(len(melody)):
        if melody[i]==-1:
            for j in range(i,i+5):
                if j<= len(melody)-1:
                    newmelody[j]=-1
    '''
    '''
    with open(".\\additionalData\\" + filename + "\\mel.dat", 'wb') as f:
        pickle.dump(melody, f)
    del melody
    #del newmelody

    strength = _export_strength(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\str.dat", 'wb') as f:
        pickle.dump(strength, f)
    del strength
    '''
    #iz = [3952.1235 / i for i in range(6, 206)]
    #cos_mat = np.array([np.cos(np.linspace(0, 3952.1235 / i, 630)) for i in range(6, 206)])

    '''
    delta = time.time()
    for i in range(len(spectrogram_db[0])//12):
        S = np.ravel(spectrogram_db[0:len(spectrogram_db), i:i+1])[:630] + 80
        a = _find_peek(S, freq)

        S_mat = np.tile(S, (200, 1))
        b = _gpt_peek(S, freq, cos_mat, S_mat)

        if a != b:
            print('shit', i)
            break
    print(time.time() - delta)
    
    
    
    
    
    
    delta = time.time()
    for i in range(len(spectrogram_db[0])):
        S = np.ravel(spectrogram_db[0:len(spectrogram_db), i:i+1])[:630] + 80
        S_mat = np.tile(S, (200, 1))
        a = _gpt_peek(S, freq, cos_mat, S_mat)
    print(time.time() - delta)
    '''


    # print(vocal_feature)
    # _plt_show(spectrogram_db)


#print('start run')

# print(len(librosa.fft_frequencies()))
file_analysis("Wild_Flower")
