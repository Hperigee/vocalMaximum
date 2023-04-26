import librosa
from spleeter.separator import Separator


class SoundFormInfo:
    def __init__(self, filename, waveform, sr):
        self.filename = filename
        self._waveform = waveform
        self._sr = sr

    def analysis(self):
        pass

def _filename_fetch():
    pass
def convert():
    pass
def inputfile(directory):
    y, sr = librosa.load(directory)
    #filename=_filename_fetch(directory)
    song = SoundFormInfo(None, y, sr)
    _seperate(directory)
    return


def _seperate(directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(directory, '.\\temp')
    return

if __name__=='__main__':
    inputfile('.\\THORNAPPLE-Blue_Spring.mp3')