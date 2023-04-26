import librosa
import spleeter
import pickle
class SoundFormInfo:
    def __init__(self,filename,waveform,sr):
        self.filename=filename
        self._waveform=_waveform
        self._sr=_sr
    def analysis(self):
        pass
def inputfile(toinput):
    filename = toinput
    y, sr = librosa.load(filename)
    song=SoundFormInfo(filename,y,sr)
    return song

def seperate(song):
    songname=song.filename
    pass