import librosa
import spleeter
class SoundFormInfo:
    def __init__(self,filename,waveform,sr):
        self.filename=filename
        self.waveform=waveform
        self.sr=sr
    def analysis(self):
        pass
def inputfile(toinput):
    filename = toinput
    y, sr = librosa.load(filename)
    song=SoundFormInfo(filename,y,sr)
    return song
