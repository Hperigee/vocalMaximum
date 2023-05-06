from  SoundFormInfo import SoundFormInfo
import pickle

testlist=[]
for i in range(1000):
    example=SoundFormInfo(f"exampleSound{i}", "artist")
    testlist.append(example)

with open(f'.\\testData\\exampleSoundList.dat', 'wb') as file:
    pickle.dump(testlist, file)
    del testlist

file.close()