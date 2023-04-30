import librosa
import librosa.display
import numpy as np
import pickle


def _plt_show(spectrogram_db):
    if __name__ == '__main__':
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        img = librosa.display.specshow(spectrogram_db, x_axis='time', y_axis='hz', ax=ax)
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        plt.xlabel('time')
        plt.ylabel('freq')

        plt.show()


def _find_peek(S, frame, max_ind):  # return list of peek frequency and dB weight
    # sorry for fckin' unstructured code

    L = []
    weight, mid_freq, ind = -1, -1, -1
    freq_list = librosa.fft_frequencies()

    for i in range(min(210, max_ind)):
        if S[i][frame] > -40.0 and S[i][frame] > S[i + 1][frame]:
            weight = S[i - 3][frame] + S[i - 2][frame] + S[i - 1][frame] + S[i][frame] + S[i + 1][frame] \
                     + S[i + 2][frame] + 80.0 * 6
            mid_freq = (freq_list[i - 3] * (S[i - 3][frame] + 80.0) + freq_list[i - 2] * (S[i - 2][frame] + 80.0)
                        + freq_list[i - 1] * (S[i - 1][frame] + 80.0) + freq_list[i] * (S[i][frame] + 80.0)
                        + freq_list[i + 1] * (S[i + 1][frame] + 80.0) + freq_list[i + 2] * (
                                    S[i + 2][frame] + 80.0)) / weight
            L.append([mid_freq, weight])
            ind = i
            break
    print(ind)
    ind = ind * 2 - 10 if ind != -1 else False

    if ind is not False:
        flag = True
        for i in range(ind, ind + 20):
            if S[i][frame] > -50.0 and S[i][frame] > S[i + 1][frame]:
                weight = S[i - 3][frame] + S[i - 2][frame] + S[i - 1][frame] + S[i][frame] + S[i + 1][frame] \
                         + S[i + 2][frame] + 80.0 * 6
                mid_freq = (freq_list[i - 3] * (S[i - 3][frame] + 80.0) + freq_list[i - 2] * (S[i - 2][frame] + 80.0)
                            + freq_list[i - 1] * (S[i - 1][frame] + 80.0) + freq_list[i] * (S[i][frame] + 80.0)
                            + freq_list[i + 1] * (S[i + 1][frame] + 80.0) + freq_list[i + 2] * (
                                        S[i + 2][frame] + 80.0)) / weight
                L.append([mid_freq, weight, 1])
                flag = False
                break
        if flag: L.append([freq_list[ind + 10], 0])
        flag = True
        ind = (ind + 10) // 2 * 3 - 10 if ind != -1 else 0

        for i in range(ind, ind + 20):
            if S[i][frame] > -50.0 and S[i][frame] > S[i + 1][frame]:
                weight = S[i - 3][frame] + S[i - 2][frame] + S[i - 1][frame] + S[i][frame] + S[i + 1][frame] \
                         + S[i + 2][frame] + 80.0 * 6
                mid_freq = (freq_list[i - 3] * (S[i - 3][frame] + 80.0) + freq_list[i - 2] * (S[i - 2][frame] + 80.0)
                            + freq_list[i - 1] * (S[i - 1][frame] + 80.0) + freq_list[i] * (S[i][frame] + 80.0)
                            + freq_list[i + 1] * (S[i + 1][frame] + 80.0) + freq_list[i + 2] * (
                                        S[i + 2][frame] + 80.0)) / weight
                L.append([mid_freq, weight, 2])
                flag = False
                break
        if flag: L.append([freq_list[ind + 10], 0])

    return L  # [] or [[...], [...], [...]]


def _export_melody(vocal_feature):
    L = []  # L[frame] -> hz  or  -1
    for i in vocal_feature:
        if len(i) != 0: L.append(i[0][0])
        else: L.append(-1)
    return L


def _export_strength(vocal_feature):
    L = []  # L[frame] -> strength: 0 ~ 2  or  -1
    for i in vocal_feature:
        if len(i) != 0: L.append((1 * i[1][1] + 2 * i[2][1]) / (i[0][1] + i[1][1] + i[2][1]))
        else: L.append(-1)
    return L


def file_analysis(filename, max_hz):
    song_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    raw_wave, sr = librosa.load(song_directory)
    spectrogram_db = librosa.stft(y=raw_wave)
    spectrogram_db = librosa.amplitude_to_db(np.abs(spectrogram_db), ref=np.max)
    # spectrogram_db[level][frame]
    # 1 frame == 512 / sr=22050 sec
    # use librosa.fft_frequencies() to learn

    freq_list = librosa.fft_frequencies()
    max_ind = 222
    for i in range(len(freq_list)):
        if freq_list[i] > max_hz:
            max_ind = i
            break

    vocal_feature = []
    for i in range(len(spectrogram_db[0])):
        vocal_feature.append(_find_peek(spectrogram_db, i, max_ind))
    # now vocal_feature has 3 harmonics hz and dB of vocal with format: vocal_feature[frame][1~3rd harmonics]

    melody = _export_melody(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\mel.dat", 'wb') as f:
        pickle.dump(melody, f)
    del melody

    strength = _export_strength(vocal_feature)
    with open(".\\additionalData\\" + filename + "\\str.dat", 'wb') as f:
        pickle.dump(strength, f)
    del strength

    #  _plt_show(spectrogram_db)


#file_analysis("THORNAPPLE-Blue_Spring", 1661)