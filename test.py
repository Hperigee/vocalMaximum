from  SoundFormInfo import SoundFormInfo
import pickle

example=SoundFormInfo("exampleSound", "artist1")

with open('exampleSound.dat', 'wb') as file:
    pickle.dump(example, file)
    del example

file.close()