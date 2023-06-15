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


global STOP
STOP = False


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


def _export_melody(vocal_feature):
    L = []  # L[frame] -> hz  or  -1
    for i in vocal_feature:
        if len(i) != 0: L.append(np.log2(i[1][0]/130.8128))
        else: L.append(-1)
    return L


def _export_strength(vocal_feature):
    L = []  # L[frame] -> strength: 0 ~ 2  or  -1
    e = 120
    for i in vocal_feature:
        if len(i) != 0 and i[0][1] + i[1][1] + i[2][1] != 0:
            a = 0 if i[0][1] < e else i[0][1] - e
            b = 0 if i[1][1] < e else i[1][1] - e
            c = 0 if i[2][1] < e else i[2][1] - e
            if a + b + c != 0:
                L.append((b + 2 * c) / (a + b + c))
            else: L.append(-1)
        else: L.append(-1)
    return L
    
    
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


def breath(L):  # L: melody, fx -> 한호흡 최대 길이
    mx = 0
    last = 0
    cmp = [-1, -1, -1]
    for i in range(len(L)):
        if L[i:i+3] == cmp:
            mx = max(mx, i - last)
    return round(mx * 512 / 22050, 3)


def health(melody):

    mx = 0
    now = 0
    e = 0.5

    for i in range(len(melody)):
        if melody[i] != -1: now += melody[i]

        now -= e

        if now < 0: now = 0

        mx = max(mx, now)

    return round(mx / 1000, 3)


def file_analysis(vocal_waveform, filename):

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

    ###############
    '''
    xs = [i * 512 / 22050 for i in range(len(melody))]
    plt.plot(xs, melody, 'ro', ms=2.0)
    plt.plot(xs, strength, 'bo', ms=2.0)
    plt.show()
    '''
    ###############

    expression = round(express(strength),2)
    highest, original = highest_note(melody)
    range_of_note = round(note_range(melody),2)
    breath_hd = breath(melody)
    health_hd = health(melody)
    adv_data = SoundFormInfo.AdvancedInfo(expression, highest, original, range_of_note, breath_hd, health_hd)


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


def _mel_similarity(new, original, frame):  # 비슷하면 0, new가 낮으면 -1, 반대면 1
    if new == -1: return 0

    # 비슷하다 == 100cent(=1키) 차이 이내
    e = np.float(1)/12

    search = np.array(original[max(frame - 4, 0) : min(frame + 5, len(original))])
    search = np.tile(np.array([new]), len(search)) - search
    cond = list(np.abs(search) <= e)
    fit = cond.count(True)
    if fit > len(search) / 3: return 0

    cnt = 0
    for i in search:
        if i < 0: cnt += 1

    res = -1 if cnt > len(search) / 2 else 1
    return res


def _str_similarity(new, original, frame):  # 비슷하면 0, new가 여리면 -1, 진하면 1
    if new == -1: return 0

    # 비슷하다 == ??
    e = np.float(1)/4

    search = np.array(original[max(frame - 4, 0): min(frame + 5, len(original))])
    search = np.tile(np.array([new]), len(search)) - search
    cond = list(np.abs(search) <= e)
    fit = cond.count(True)
    if fit > len(search) / 3: return 0

    cnt = 0
    for i in search:
        if i < 0: cnt += 1

    res = -1 if cnt > len(search) / 2 else 1
    return res


def _find_can_max(logs):
    e = np.float(1)/8

    logs = [i[0][0] if i[1][0] > 0.5 else -1 for i in logs]
    logs.sort(key=lambda x: -x)

    for i in range(2, len(logs)):
        if logs[i-2] - logs[i] < e and logs[i-1] - logs[i] < e: return logs[i]

    return -1


def _find_well_max(logs):
    e = np.float(1)/8

    logs = [i[0][0] if i[1][1] == 0 else -1 for i in logs]
    logs.sort(key=lambda x: -x)

    for i in range(2, len(logs)):
        if logs[i - 2] - logs[i] < e and logs[i - 1] - logs[i] < e: return logs[i]

    return -1


def _find_health_max(logs):
    melody = [i[0][0] for i in logs]

    mx = 0
    now = 0
    e = 0.5

    for i in range(len(melody)):
        if melody[i] != -1: now += melody[i]

        now -= e

        if now < 0: now = 0

        mx = max(mx, now)

    return round(mx / 1000, 3)


def _sec_to_frame(sec):
    DEFAULT_OFFSET = -8
    return int(sec * 22050 / 512) + DEFAULT_OFFSET


def live_analysis(filename, display_Queue, offset, startSec, endSec, res_que):

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

    logs = []
    bee = ['도 ', '도#', '레 ', '레#', '미 ', '파 ', '파#', '솔 ', '솔#', '라 ', '라#', '시 ']
    for i in range(0, int(RATE / CHUNK * LENGTH)):
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

        if note != -1:
            note = '{0}옥 {1}'.format(int(note + 1/24), bee[int((note + 1/24) % 1 * 12)])
            if strength > 0.9: strength = '진성'
            elif strength > 0.5: strength = '여린 진성'
            else: strength = '가성'

            if note_feedback == 0: note_feedback = '정확해요'
            elif note_feedback == -1: note_feedback = '더 높게'
            elif note_feedback == 1: note_feedback = '더 낮게'

            if str_feedback == 0: str_feedback = '정확해요'
            elif str_feedback == -1: str_feedback = '더 세게'
            elif str_feedback == 1: str_feedback = '더 여리게'
        else:
            note = ':D'
            note_feedback = ':D'
            strength = ':D'
            str_feedback = ':D'

        to_display = [f'{note}\n{note_feedback}', f'{strength}\n{str_feedback}']
        display_Queue.put(to_display)

        if STOP: break



    print('record stopped')

    with open('.\\profile.dat', 'rb') as f:
        old_profile = pickle.load(f)

    old_profile.can_max = max(old_profile.can_max, _find_can_max(logs))
    old_profile.well_max = max(old_profile.well_max, _find_well_max(logs))
    old_profile.verified_health = max(old_profile.verified_health, _find_health_max(logs))

    with open('.\\profile.dat', 'wb') as f:
        pickle.dump(old_profile, f)

    sim_mel = [i[0][1] == 0 for i in logs].count(True) / len(logs)
    sim_str = [i[1][1] == 0 for i in logs].count(True) / len(logs)
    score = round(60 + 42 * sim_mel + 6 * sim_str, 3)
    if score > 100: score = 100
    sim_str *= 1.2
    if sim_str > 1: sim_str = 1
    try:
        os.makedirs('./temp')
    except:
        pass
    with open('./temp/result','wb') as f:
        pickle.dump(f'참 잘했어요~\n\n점수 : {score}\n\n표현 : {round(sim_str * 100, 3)}', f)

    stream.stop_stream()
    stream.close()
    p.terminate()

    f1 = plt.plot
    f2 = plt.show
    p1 = (list(range(len(logs) * 4)), np.repeat([i[0][0] for i in logs], 4), 'go')
    p2 = (list(range(len(logs) * 4)), origin_mel[_sec_to_frame(startSec):_sec_to_frame(startSec) + len(logs) * 4], 'ro')

    return (f1, f2, p1, p2)


#print('start run')
if __name__=="__main__":
    #print(len(librosa.fft_frequencies()))
    #file_analysis('')
    #live_analysis('에일리-첫눈처럼_너에게_가겠다')
    pass