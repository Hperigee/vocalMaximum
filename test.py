from  SoundFormInfo import SoundFormInfo
import pickle

for i in range(100):
    example=SoundFormInfo(f"exampleSound{i}", "artist")

    with open(f'.\\testData\\exampleSound{i}.dat', 'wb') as file:
        pickle.dump(example, file)
        del example

    file.close()