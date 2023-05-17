class Profile:
    def __init__(self):
        self.well_max = 0
        self.can_max = 0
        self.verified_health = 0
        self.offset = 0

if __name__ == '__main__':
    import pickle

    new = Profile()

    with open('.\\profile0.dat', 'wb') as f:
        pickle.dump(new, f)