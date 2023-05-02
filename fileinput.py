import librosa
import os
import analysis

from spleeter.separator import Separator
from pydub import AudioSegment


class SoundFormInfo:
    def __init__(self, filename):
        self.filename = filename
        self.notes = None  # 시간에 따른 음높이
        self.express = None  # 시간에 따른 표현도
        self.highest_note = None  # 최고음
        self.note_range = None  # 음역 비중
        self.rhythm_hd = None  # 박자감
        self.breath_hd = None  # 호흡 지수
        self.health = None  # 체력 지수


def _wav_to_mp3(filename):
    directory = ".\\temp\\" + filename + '\\aaaaaaaaa.wav'
    origin = AudioSegment.from_wav(directory)
    origin.export(".\\additionalData\\" + filename + "\\" + filename + '.mp3', format='mp3')


def _filename_fetch(directory):
    assert isinstance(directory, str)
    ind = directory.rfind('\\')
    return directory[ind + 1:-4]


def _separate(directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(directory, '.\\temp')
    return


def _remove_vocal_file(filename):
    remove_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    os.remove(remove_directory)
    return


def input_file(directory):
    _separate(directory)  # 음원 분리

    filename = _filename_fetch(directory)
    analysis.analysis(filename)  # 보컬 정보 추출

    _remove_vocal_file(filename)
    return


if __name__ == '__main__':
    safd = input_file('')
