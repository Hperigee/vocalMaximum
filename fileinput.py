import datetime
import os
import analysis
import SoundFormInfo
import time
import tinytag
from spleeter.separator import Separator, AudioAdapter
import soundfile as sf
import shutil


'''
def _wav_to_mp3(filename):
    directory = "./temp/" + filename + '/accompaniment.wav'
    origin = AudioSegment.from_wav(directory)
    os.mkdir('./additionalData/' + filename)
    new_file = './additionalData/' + filename + '/' + filename + '.mp3'
    origin.export(new_file, format='mp3')
    os.remove(directory)
    return
'''

def filename_fetch(directory):
    directory = os.path.abspath(directory)  # Convert to absolute path
    filename = os.path.basename(directory)[:-4]
    return filename, directory

def rename_directory(old_name, new_name):
    try:
        os.rename(old_name, new_name)
    except :
        pass
    return

def _separate(directory,filename,spl):

    audio_adapter = AudioAdapter.default()
    raw_wave, _ = audio_adapter.load(directory)
    stems = spl.separate(raw_wave)
    accompaniment = stems["accompaniment"]
    vocal = stems["vocals"]

    directory = f'./additionalData/{filename}/'

    if os.path.exists(directory):
        shutil.rmtree(directory)
    try:
        os.makedirs(directory)
    except:
        pass
    new_file = f'./additionalData/{filename}/{filename}.mp3'
    new_file = os.path.abspath(new_file)
    sf.write(new_file, accompaniment, samplerate=44100, format="MP3")

    #temp = f'./additionalData/{filename}/{filename}_temp.mp3'
    #sf.write(temp, vocal, samplerate=44100, format="MP3")

    del accompaniment
    return vocal

'''
def _remove_tmp(filename):
    remove_directory = './temp/' + filename
    rmtree(remove_directory)
    return
'''


def _export_basic_info(directory, filename):
    file_path = directory
    audio = tinytag.TinyTag.get(file_path)
    metadata = str(datetime.timedelta(seconds=audio.duration))[2:-7]
    name=filename.split('-')[1].strip()
    artist=filename.split('-')[0].strip()
    return SoundFormInfo.SoundFormInfo(name,
                                       artist,
                                       metadata)




def input_file(directory,spl):

    filename, abs_directory= filename_fetch(directory)
    res = _export_basic_info(abs_directory, filename)
    try:
        os.makedirs('./OriginalSong/')
    except:
        pass
    shutil.copy(abs_directory, f'./OriginalSong/')
    vocal_waveform = _separate(directory,filename,spl)  # 음원 분리

    analysis.file_analysis(vocal_waveform,filename)  # 보컬 정보 추출

    return res


if __name__ == '__main__':
    GLOBAL_SPLITTER = Separator('spleeter:2stems', stft_backend='tensorflow', multiprocess=False)
    ti=time.time()
    input_file('./박효신-야생화.mp3',GLOBAL_SPLITTER)
    print(time.time()-ti)

