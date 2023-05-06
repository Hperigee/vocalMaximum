class SoundFormInfo:
    def __init__(self,filename, artist):
        self.name = filename
        self.artist=artist
        self.duration='10:00'
        self.notes = None  # 시간에 따른 음높이
        self.express = None  # 시간에 따른 표현도
        self.highest_note = None  # 최고음
        self.note_range = None  # 음역 비중
        self.rhythm_hd = None  # 박자감
        self.breath_hd = None  # 호흡 지수
        self.health = None  # 체력 지수
