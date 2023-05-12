import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time
from collections import Counter
import os
import SoundFormInfo
import pyaudio
import Profile



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
def _show_output(melody,strength):
    timeline = np.arange(len(melody)) * 512 / 22050
    plt.plot(timeline, melody, 'ro', ms=2)
    plt.plot(timeline, strength, 'bo', ms=2)
    plt.show()

def _gpt_peek(S, freq, cos_mat, S_mat):
    result = np.zeros(630)
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
        if len(i) != 0: L.append(np.log2(i[1][0]/130.8128))
        else: L.append(-1)
    return L


def _export_strength(vocal_feature):
    L = []  # L[frame] -> strength: 0 ~ 2  or  -1
    for i in vocal_feature:
        if len(i) != 0 and i[0][1] + i[1][1] + i[2][1] != 0:
            L.append((i[1][1] + 2 * i[2][1]) / (i[0][1] + i[1][1] + i[2][1]))
        else: L.append(-1)
    return L


def _denoise(S, threshold):
    S = np.array(S)  # melody
def express(L):
    filtered_list = list(filter(lambda x: x != -1, L))
    return 40*np.std(filtered_list)

def highest_note(lst):
    counter = Counter(lst)
    max_repeated_value = max([value for value, count in counter.items() if count >= 8])
    return max_repeated_value

def convert_to_octave(a):
    scale = int(a*12 + 0.5)
    octave = scale//12
    note = scale%12
    A = ['도','도#','레','레#','미','파','파#','솔','솔#','라','라#','시']
    return str(f'{octave}옥 '+ A[note])

def note_range(L):
    filtered_list = list(filter(lambda x: x != -1, L))
    mean=np.mean(filtered_list)
    return float(mean)

def breath():
    return "develop"

def health():
    return "develop"
def file_analysis(vocal_waveform,filename):

    delta = time.time()

    if vocal_waveform.ndim > 1:
        vocal_waveform = np.mean(vocal_waveform, axis=1)
    raw_wave = librosa.resample(vocal_waveform, 44100, 22050)
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

    print("processed", time.time() - delta)
    delta = time.time()

    melody = _export_melody(vocal_feature)
    strength = _export_strength(vocal_feature)
    expression = round(express(strength),2)
    highest = highest_note(melody)
    range_of_note = round(note_range(melody),2)
    breath_hd = breath()
    health_hd = health()
    adv_data = SoundFormInfo.AdvancedInfo(expression,highest,range_of_note,breath_hd,health_hd)


    print("exported", time.time() - delta)

    #_show_output(melody,strength)

    folder_path = f"./additionalData/{filename}"

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        pass


    with open(".\\additionalData\\" + filename + "\\mel.dat", 'wb') as f:
        pickle.dump(melody, f)
    f.close()
    del melody

    with open(".\\additionalData\\" + filename + "\\str.dat", 'wb') as f:
        pickle.dump(strength, f)
    del strength
    f.close()
    with open(".\\additionalData\\" + filename + "\\adv.dat", 'wb') as f:
        pickle.dump(adv_data, f)
    del adv_data
    f.close()
    del raw_wave
    del cos_mat
    del spectrogram_db
    del freq


    #iz = [3952.1235 / i for i in range(6, 206)]
    #cos_mat = np.array([np.cos(np.linspace(0, 3952.1235 / i, 630)) for i in range(6, 206)])

    # print(vocal_feature)
    # _plt_show(spectrogram_db)
    return


def _mel_similarity(new: float, original: list, frame, offset_fr):  # 비슷하면 0, new가 낮으면 -1, 반대면 1
    # 비슷하다 = 150cent(=1.5키) 차이 이내
    e = np.float(1)/8

    search = np.array(original[np.max(offset_fr + frame - 4, 0):np.min(offset_fr + frame + 5, len(original))])
    search = np.tile(np.array([new]), len(search)) - search
    if np.min(np.abs(search)) < e: return 0

    cnt = 0
    for i in search:
        if i < 0: cnt += 1

    res = -1 if cnt > len(search) / 2 else 1
    return res


def _find_can_max(logs):
    e = np.float(1)/8

    logs = [i[0] for i in logs]
    logs.sort(key=lambda x: -x)

    for i in range(1, len(logs)):
        if logs[i-1] - logs[i] < e: return logs[i]

    return -1


def live_analysis(filename, ):

    with open(f'.\\additionalData\\{filename}\\mel.dat', 'rb') as f:
        origin_mel = pickle.load(f)
    with open(f'.\\additionalData\\{filename}\\str.dat', 'rb') as f:
        origin_str = pickle.load(f)

    CHUNK = 2048
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 22050

    end = 6 * np.pi * 629
    cos_mat = np.cos(np.array([np.linspace(0, end / i, 630) for i in range(18, 630)]))
    freq = librosa.fft_frequencies()

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=4)

    print('start recording')

    to_display = []
    logs = []
    bee = ['도 ', '도#', '레 ', '레#', '미 ', '파 ', '파#', '솔 ', '솔#', '라 ', '라#', '시 ']
    seconds = 5
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        stt = time.time()

        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.amplitude_to_db(np.abs(librosa.stft(y=data, hop_length=4096)), ref=256)
        data = np.ravel(data)[:630] + 80
        data[data[np.arange(630)] < 0] = 0

        data_mat = np.tile(data, (612, 1))
        vocal_feature = [_gpt_peek(data, freq, cos_mat, data_mat)]
        note = _export_melody(vocal_feature)[0]
        strength = _export_strength(vocal_feature)[0]

        logs.append([note])

        # note = _mel_similarity(note, origin_mel, _get_frame(), offset_fr)

        if note != -1: note = '{0}옥 {1}'.format(int(note + 1/24), bee[int((note + 1/24) % 1 * 12)])
        else: note = ':D     '
        to_display = [note, 'dev-ing']
        #print(to_display, (time.time() - stt) * 1000)

        if FLAG == True: break


    print('record stopped')

    with open('.\\profile.dat', 'rb') as f:
        old_profile = pickle.load(f)

    old_profile.can_max = max(old_profile.can_max, _find_can_max(logs))

    with open('.\\profile.dat', 'wb') as f:
        pickle.dump(old_profile, f)

    stream.stop_stream()
    stream.close()
    p.terminate()


#print('start run')
if __name__=="__main__":
    #print(len(librosa.fft_frequencies()))
    #file_analysis("닐로 - 지나오다")
    #live_analysis('소찬휘-Tears')
    '''
    audio = pyaudio.PyAudio()

    for index in range(audio.get_device_count()):
        desc = audio.get_device_info_by_index(index)
        print("DEVICE: {device}, INDEX: {index}, RATE: {rate} ".format(
            device=desc["name"], index=index, rate=int(desc["defaultSampleRate"])))
    '''
    with open('.\\profile.dat', 'wb') as f:
        sdf = Profile.Profile()
        pickle.dump(sdf, f)