class SoundFormInfo:
    def __init__(self, filename, artist, duration):
        self.name = filename
        self.artist = artist
        self.duration = duration


class AdvancedInfo:
    def __init__(self, express, highest_note, original, note_range, breath_hd, health):
        self.express = express  # 시간에 따른 표현도 : str 분산
        self.highest_note = highest_note  # 최고음 : max height (3점 이상)
        self.highest_note_num = original
        self.note_range = note_range  # 음역 비중 : 무게 중심
        self.breath_hd = breath_hd  # 호흡 지수 : max(-1 간격)
        self.health = health  # 체력 지수 : mel - 상수 * frame 의 적분 peek




