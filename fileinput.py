import datetime
import os
import analysis
import SoundFormInfo
from shutil import rmtree
import tinytag
from spleeter.separator import Separator

def _wav_to_mp3(filename):
    from pydub import AudioSegment
    directory = "./temp/" + filename + '/accompaniment.wav'
    origin = AudioSegment.from_wav(directory)
    os.mkdir('./additionalData/' + filename)
    new_file = './additionalData/' + filename + '/' + filename + '.mp3'
    origin.export(new_file, format='mp3')
    os.remove(directory)


def _filename_fetch(directory):
    filename = os.path.basename(directory)
    filename[:-4]
    return filename

def rename_directory(old_name, new_name):
    try:
        os.rename(old_name, new_name)
    except :
        pass

def _separate(directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(directory, './temp',)
    return


def _remove_tmp(filename):
    remove_directory = './temp/' + filename
    rmtree(remove_directory)
    return



def _export_basic_info(directory, filename):
    file_path = directory
    audio = tinytag.TinyTag.get(file_path)
    metadata = str(datetime.timedelta(seconds=audio.duration))[2:-7]
    name=filename.split('-')[1].strip()
    artist=filename.split('-')[0].strip()[46:]
    return SoundFormInfo.SoundFormInfo(name,
                                       artist,
                                       metadata)




def input_file(directory):

    filename = _filename_fetch(directory)
    print(filename)
    res = _export_basic_info(directory, filename)

    _separate(directory)  # 음원 분리
    _wav_to_mp3(filename)   # MR은 따로 저장 / wav 삭제

    analysis.file_analysis(filename)  # 보컬 정보 추출

    _remove_tmp(filename)  # tmp 삭제
    return res


if __name__ == '__main__':
    import time

    stt = time.time()
    input_file('.\\닐로-지나오다.mp3')
    stt = time.time() - stt
    print(stt, 'seconds')

