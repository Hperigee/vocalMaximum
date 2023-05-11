import datetime
import os
import analysis
import SoundFormInfo
import time
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
    return


def _filename_fetch(directory):
    directory = os.path.abspath(directory)  # Convert to absolute path
    filename = os.path.basename(directory)[:-4]
    return filename, directory

def rename_directory(old_name, new_name):
    try:
        os.rename(old_name, new_name)
    except :
        pass
    return

def _separate(directory,spl):
    spl.separate_to_file(directory, './temp')
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
    artist=filename.split('-')[0].strip()
    return SoundFormInfo.SoundFormInfo(name,
                                       artist,
                                       metadata)




def input_file(directory,spl):

    filename, abs_directory= _filename_fetch(directory)
    res = _export_basic_info(abs_directory, filename)
    _separate(directory,spl)  # 음원 분리
    _wav_to_mp3(filename)   # MR은 따로 저장 / wav 삭제

    analysis.file_analysis(filename)  # 보컬 정보 추출
    _remove_tmp(filename)  # tmp 삭제
    return res


if __name__ == '__main__':
    GLOBAL_SPLITTER = Separator('spleeter:2stems', stft_backend='tensorflow', multiprocess=False)
    ti=time.time()
    input_file('./박효신-야생화.mp3',GLOBAL_SPLITTER)
    print(time.time()-ti)

