from  SoundFormInfo import SoundFormInfo
import pickle
import random
import string

def generate_random_string(length):
    # Define the characters to choose from
    characters = string.ascii_letters + string.digits  # includes uppercase letters, lowercase letters, and digits

    # Generate the random string
    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string

testlist=[]
for i in range(10):
    example=SoundFormInfo(generate_random_string(10), generate_random_string(5),"10:00")
    testlist.append(example)

testlist.sort(key=lambda x: x.name)

with open(f'.\\testData\\exampleSoundList.dat', 'wb') as file:
    pickle.dump(testlist, file)
    del testlist

file.close()