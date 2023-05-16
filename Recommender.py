import os
import pickle


def can_sing():
    with open('.\\profile.dat', 'rb') as f:
        profile = pickle.load(f)

    song_list = os.listdir('.\\additionalData')
    del song_list[song_list.index('test.txt')]

    return_list = []

    for i in song_list:
        with open(f'.\\additionalData\\{i}\\adv.dat', 'rb') as f:
            song_data = pickle.load(f)
        if song_data.highest_note_num <= profile.can_max: return_list.append(i)

    return return_list


def well_sing():  # well_max,
    with open('.\\profile.dat', 'rb') as f:
        profile = pickle.load(f)

    song_list = os.listdir('.\\additionalData')
    del song_list[song_list.index('test.txt')]

    return_list = []

    for i in song_list:
        with open(f'.\\additionalData\\{i}\\adv.dat', 'rb') as f:
            song_data = pickle.load(f)
        if song_data.highest_note_num <= profile.well_max and\
            song_data.health <= profile.verified_health: return_list.append(i)

    return return_list


def barely_sing():
    with open('.\\profile.dat', 'rb') as f:
        profile = pickle.load(f)

    song_list = os.listdir('.\\additionalData')
    del song_list[song_list.index('test.txt')]

    return_list = []

    h_e = 1 / 6

    for i in song_list:
        with open(f'.\\additionalData\\{i}\\adv.dat', 'rb') as f:
            song_data = pickle.load(f)
        if song_data.highest_note_num <= profile.can_max + h_e and \
            song_data.note_range <= profile.can_max - 0.5: return_list.append(i)

    return return_list
