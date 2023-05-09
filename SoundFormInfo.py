class SoundFormInfo:
    def __init__(self,filename, artist, duration):
        self.name = filename
        self.artist = artist
        self.duration = duration


class AdvancedInfo:
    def __init__(self,filename, artist):
        self.express = None  # 시간에 따른 표현도 : str 분산
        self.highest_note = None  # 최고음 : max height (3점 이상)
        self.note_range = None  # 음역 비중 : 무게 중심
        self.breath_hd = None  # 호흡 지수 : max(-1 간격)
        self.health = None  # 체력 지수 : mel - 상수 * frame 의 적분 peek