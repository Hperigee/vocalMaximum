import librosa
import librosa.display
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


def _find_peek(S, frame):  # return list of peek frequency and dB weight

    threshold = -40

    freq_list = librosa.fft_frequencies()

    peak_sound = [0] * 1025
    for i in range(6, 206):
        j=i
        while j<1025:
            if 6<j-2*i and j+2*i<1025:
                if S[j][frame]+S[j+i][frame]+S[j-i][frame]+S[j+2*i][frame]+S[j-2*i][frame] >(-59*5) :
                    peak_sound[j] += 1
            j+=i

    first_max=peak_sound.index(max(peak_sound))
    peak_sound.pop(first_max)
    second_max = peak_sound.index(max(peak_sound))
    peak_sound.pop(second_max)
    second_max+=1

    '''
    indexList = []
    if sum(peak_sound) <= 20:
        return []
    for i in range(len(peak_sound)):
        if len(indexList) < 2 and peak_sound[i] > 0:
            indexList.append(i)
    bass_freq_ind = indexList[1] - indexList[0]
    '''
    bass_freq_ind= abs(first_max-second_max)

    bass_ind = bass_freq_ind + 6
    #print(bass_ind)
    if 3*bass_ind>200: return []

    if bass_ind: return [[freq_list[bass_ind], S[bass_ind][frame]],
                         [freq_list[2 * bass_ind], S[2 * bass_ind][frame]],
                         [freq_list[3 * bass_ind], S[3 * bass_ind][frame]]]
    # [] or [[hz, dB], [hz, dB], [hz, dB]]


def _export_melody(vocal_feature):
    L = []  # L[frame] -> hz  or  -1
    for i in vocal_feature:
        if len(i) != 0:
            L.append(i[1][0])
        else:
            L.append(-1)
    return L


def _export_strength(vocal_feature):
    L = []  # L[frame] -> strength: 0 ~ 2  or  -1
    for i in vocal_feature:
        if len(i) != 0:
            L.append((1 * i[1][1] + 2 * i[2][1]) / (i[0][1] + i[1][1] + i[2][1]))
        else:
            L.append(-1)
    return L


def file_analysis(filename):
    song_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    y, sr = librosa.load(song_directory)
    raw_wave = librosa.resample(y, orig_sr=sr, target_sr=11025)
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
    '''
    print(len(melody))
    newmelody=copy.deepcopy(melody)
    for i in range(len(melody)):
        if melody[i]==-1:
            for j in range(i,i+5):
                if j<= len(melody)-1:
                    newmelody[j]=-1
    '''

    with open(".\\additionalData\\" + filename + "\\mel.dat", 'wb') as f:
        pickle.dump(melody, f)
    del melody
    # del newmelody

    strength = _export_strength(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\str.dat", 'wb') as f:
        pickle.dump(strength, f)
    del strength

    print(time.time() - delta)

    # _plt_show(spectrogram_db)


print('start run')
delta = time.time()

# print(len(librosa.fft_frequencies()))
file_analysis("Wild_Flower")
