import datetime

import librosa
import os
import analysis
import SoundFormInfo

from spleeter.separator import Separator
from pydub import AudioSegment
from shutil import rmtree
from mutagen.mp3 import MP3


def _wav_to_mp3(filename):
    directory = "./temp/" + filename + '/accompaniment.wav'
    origin = AudioSegment.from_wav(directory)
    os.mkdir('./additionalData/' + filename)
    new_file = './additionalData/' + filename + '/' + filename + '.mp3'
    origin.export(new_file, format='mp3')
    os.remove(directory)


def _filename_fetch(directory):
    assert isinstance(directory, str)
    ind = directory.rfind('\\')
    return directory[ind + 1:-4]


def _separate(directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(directory, './temp')
    return


def _remove_tmp(filename):
    remove_directory = './temp/' + filename
    rmtree(remove_directory)
    return


def _export_basic_info(directory, filename):
    dash_index = filename.find('-')
    metadata = str(datetime.timedelta(seconds=MP3(directory).info.length))
    return SoundFormInfo.SoundFormInfo(filename[dash_index + 1:],
                                      filename[:dash_index],
                                      metadata[2:metadata.rfind('.')])


def input_file(directory):

    filename = _filename_fetch(directory)

    res = _export_basic_info(directory, filename)

    #separate(directory)  # 음원 분리
    #wav_to_mp3(filename)   # MR은 따로 저장 / wav 삭제

    #analysis.file_analysis(filename)  # 보컬 정보 추출

    #_remove_tmp(filename)  # tmp 삭제
    return res


if __name__ == '__main__':
    import time

    stt = time.time()
    input_file('.\\성시경-너의_모든_순간.mp3')
    stt = time.time() - stt
    print(stt, 'seconds')

