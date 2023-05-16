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


def _show_output(melody,strength):
    timeline = np.arange(len(melody)) * 512 / 22050
    plt.plot(timeline, melody, 'ro', ms=2)
    plt.plot(timeline, strength, 'bo', ms=2)
    plt.show()
    

def _find_peek(S, freq, cos_mat, S_mat):
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

def _find_frame():
    import random
    return random.random()

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

    return convert_to_octave(max_repeated_value), max_repeated_value


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
        vocal_feature.append(_find_peek(S, freq, cos_mat, S_mat))
    # now vocal_feature has 3 harmonics hz and dB of vocal with format:
    # vocal_feature[frame][1~3rd harmonics] -> [hz, dB sum of near hz]

    print("processed", time.time() - delta)
    delta = time.time()

    melody = _export_melody(vocal_feature)
    strength = _export_strength(vocal_feature)
    expression = round(express(strength),2)
    highest ,original= highest_note(melody)
    range_of_note = round(note_range(melody),2)
    breath_hd = breath()
    health_hd = health()
    adv_data = SoundFormInfo.AdvancedInfo(expression,highest,original,range_of_note,breath_hd,health_hd)


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

    # _plt_show(spectrogram_db)
    return


######################################################################################################################


def _mel_similarity(new: float, original: list, frame):  # 비슷하면 0, new가 낮으면 -1, 반대면 1
    # 비슷하다 == 150cent(=1.5키) 차이 이내
    e = np.float(1)/8

    search = np.array(original[np.max(frame - 4, 0):np.min(frame + 5, len(original))])
    search = np.tile(np.array([new]), len(search)) - search
    if np.min(np.abs(search)) < e: return 0

    cnt = 0
    for i in search:
        if i < 0: cnt += 1

    res = -1 if cnt > len(search) / 2 else 1
    return res


def _str_similarity(new: float, original: list, frame):  # 비슷하면 0, new가 여리면 -1, 진하면 1
    # 비슷하다 == ??
    e = np.float(1)/8

    search = np.array(original[np.max(frame - 4, 0):np.min(frame + 5, len(original))])



def _find_can_max(logs):
    e = np.float(1)/8

    logs = [i[0] for i in logs]
    logs.sort(key=lambda x: -x)

    for i in range(1, len(logs)):
        if logs[i-1] - logs[i] < e: return logs[i]

    return -1


def _sec_to_frame(sec):
    return sec * 22050 / 512


def live_analysis(filename, display_Queue, offset, startSec, endSec):

    with open(f'.\\additionalData\\{filename}\\mel.dat', 'rb') as f:
        origin_mel = pickle.load(f)
    with open(f'.\\additionalData\\{filename}\\str.dat', 'rb') as f:
        origin_str = pickle.load(f)

    CHUNK = 2048
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 22050
    LENGTH = endSec - startSec

    end = 6 * np.pi * 629
    cos_mat = np.cos(np.array([np.linspace(0, end / i, 630) for i in range(18, 630)]))
    freq = librosa.fft_frequencies()

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=1)

    print('start recording')

    # 음악 재생 at startSec * 1000

    music_start_time = time.time()

    to_display = []
    logs = []
    bee = ['도 ', '도#', '레 ', '레#', '미 ', '파 ', '파#', '솔 ', '솔#', '라 ', '라#', '시 ']
    seconds = 12345
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        played_time = time.time() - music_start_time
        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.amplitude_to_db(np.abs(librosa.stft(y=data, hop_length=4096)), ref=256)
        data = np.ravel(data)[:630] + 80
        data[data[np.arange(630)] < 0] = 0

        data_mat = np.tile(data, (612, 1))
        vocal_feature = [_find_peek(data, freq, cos_mat, data_mat)]
        note = _export_melody(vocal_feature)[0]
        strength = _export_strength(vocal_feature)[0]

        frame_to_cmp = _sec_to_frame(startSec + played_time - offset * 0.001)
        note_feedback = _mel_similarity(note, origin_mel, frame_to_cmp)
        str_feedback = _str_similarity(strength, origin_str, frame_to_cmp)

        logs.append([[note, note_feedback], [strength, str_feedback]])

        if note != -1: note = '{0}옥 {1}'.format(int(note + 1/24), bee[int((note + 1/24) % 1 * 12)])
        else: note = ':D     '
        to_display = [note, 'dev-ing']
        display_Queue.append(to_display)



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
    print(librosa.fft_frequencies()[210])
