import librosa
import librosa.display
import numpy as np
import pickle
import time


def _plt_show(spectrogram_db):
    if __name__ == '__main__':
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        img = librosa.display.specshow(spectrogram_db, x_axis='time', y_axis='hz', ax=ax)
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.xlabel('time')
        plt.ylabel('freq')

        plt.show()


def _score_func(L):
    return sum(L) / len(L)


def _find_peek(S, frame):  # return list of peek frequency and dB weight

    threshold = -70.0  # constant

    freq_list = librosa.fft_frequencies()
    scores = [0] * 200
    para_list = []

    for i in range(6, 206):

        for j in range(i, 24 * i + 1, i):
            if j < 1024: para_list += [S[j-1][frame], S[j][frame], S[j+2][frame]]
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


def file_analysis(filename):
    song_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    raw_wave, sr = librosa.load(song_directory)
    spectrogram_db = librosa.stft(y=raw_wave)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram_db), ref=np.max)
    # spectrogram_db[level][frame]
    # 1 frame == 512 / sr=22050 sec
    # use librosa.fft_frequencies() to learn
    '''
    freq_list = librosa.fft_frequencies()
    max_ind = 222
    for i in range(len(freq_list)):
        if freq_list[i] > max_hz:
            max_ind = i
            break
    '''

    vocal_feature = []
    for i in range(len(spectrogram_db[0])):
        vocal_feature.append(_find_peek(spectrogram_db, i))
    # now vocal_feature has 3 harmonics hz and dB of vocal with format: vocal_feature[frame][1~3rd harmonics]

    melody = _export_melody(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\mel.dat", 'wb') as f:
        pickle.dump(melody, f)
    del melody

    strength = _export_strength(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\str.dat", 'wb') as f:
        pickle.dump(strength, f)
    del strength

    print(time.time()-delta)

    _plt_show(spectrogram_db)


print('start run')
delta = time.time()

# print(len(librosa.fft_frequencies()))
file_analysis("Wild_Flower")