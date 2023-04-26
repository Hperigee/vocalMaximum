import librosa


def analysis(filename):
    song_directory = '.\\temp\\' + filename + '\\' + 'vocals.wav'
    waveform, sr = librosa.load(song_directory)
    pass