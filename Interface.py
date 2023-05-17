import time

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFile, QTextStream, QTimer, QThread, pyqtSlot, pyqtSignal,QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from Resources_rc import *  # used
import pickle
import public_functions
import assets
from queue import Queue
from fileinput import input_file, filename_fetch
from spleeter.separator import Separator
from pydub import AudioSegment
import os
from Recommender import *
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
from Profile import Profile  # used
import tensorflow as tf


import test


global input_file_directory
input_file_directory=None
global to_process
to_process = Queue()
global GLOBAL_SPLITTER
GLOBAL_SPLITTER = Separator('spleeter:2stems', stft_backend='tensorflow', multiprocess=False)
global to_display
to_display = Queue()
global song_added
song_added = False
global live_analysis_result
live_analyis_result = ""

class Thread(QThread):
    analysis_result_ready = pyqtSignal(object)
    def __init__(self):
        super().__init__()
    def enqueue_files(self):
        global input_file_directory
        try:
            for file in input_file_directory:
                print(file,"input success")
                to_process.put(file)
        except:
            pass
        QTimer.singleShot(1000,self.enqueue_files)

    @pyqtSlot()
    def run(self):
        self.enqueue_files()
        while not to_process.empty():
            file = to_process.get()
            filename, _ = filename_fetch(file)
            directory_path = f'./additionalData/{filename}'
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                print("existing")
                continue
            print(file, "start process")
            res = input_file(file,GLOBAL_SPLITTER)

            with open(f'./Datas/{filename}.tmpdat', 'wb') as file:
                pickle.dump(res, file)

            self.analysis_result_ready.emit(res)

        self.finished.emit()

class RealTime(QThread):
    display_new_info = pyqtSignal(object)
    start_timer =pyqtSignal()
    display_result = pyqtSignal()
    def __init__(self,songWidget,songname,artist,startMin,startSec,stopMin,stopSec):
        super().__init__()
        self.main = window
        self.songWidget =songWidget
        self.startMin = startMin
        self.startSec = startSec
        self.stopMin = stopMin
        self.stopSec =stopSec
        self.song_name=songname
        self.artist = artist
    @pyqtSlot()
    def run(self):
        self.songWidget.record.canceled.connect(self.stop_analysis)

        guide_directory = f'./Defaults/{self.artist}-{self.song_name}.mp3'
        mr_directory = f'./additionalData/{self.artist}-{self.song_name}/{self.artist}-{self.song_name}.mp3'

        self.start = analysis_thread(self,self.startMin,self.startSec,self.stopMin,self.stopSec)

        start_time = (self.startMin * 60 + self.startSec) * 1000
        stop_time =(self.stopMin*60+self.stopSec)*1000
        temp_mr =self.export(mr_directory,start_time,stop_time,'mr')
        temp_guide = self.export(guide_directory, start_time, start_time,'guide')

        self.player = AudioPlayerThread(self, temp_mr)
        self.player2 = AudioPlayerThread(self, temp_guide)

        self.player2.start()
        self.player.start()
        self.player.song_ready.connect(self.start_timer)
        self.songWidget.record.record_start.connect(self.start_analysis)
        texts= None
        while True:
            try:
                texts = to_display.get()
            except:
                pass
            if texts == 'STOP':
                break
            #print(texts)
            self.display_new_info.emit(texts)

        self.finished.emit()
    def export(self,file_path,start_time, finish_time,label):
        audio = AudioSegment.from_file(file_path, format="mp3")
        if start_time < 3000:
            extension = 3000 - start_time
            audio_segment_temp = AudioSegment.silent(duration=extension) + audio
            audio_segment = audio_segment_temp[start_time:finish_time]
            print(len(audio_segment))
        else:
            audio_segment = audio[start_time - 3000:finish_time]
        audio_segment_final = AudioSegment()
        for i in range(1000):
            audio_segment_final = audio_segment[i:i+1] - (audio_segment[i:i+1].dBFS * (0.0003*i)) + audio_segment_final
        audio_segment = audio_segment[1000:3000] - (audio_segment[1000:3000].dBFS * (0.3)) + audio_segment[3000:]

        self.temp_file = f"./temp/temp_audio_{label}.mp3"
        audio_segment.export(self.temp_file, format="mp3")
        return self.temp_file

    def start_analysis(self):
        self.start.start()

    def stop_analysis(self):
        test.STOP = True # flag
        to_display.put("STOP")
        #print("stopped")
    def timer(self):
        self.start_timer.emit()

class AudioPlayerThread(QThread):
    song_ready = pyqtSignal()
    def __init__(self,checking_thread,temp_file):
        super(AudioPlayerThread, self).__init__()
        checking_thread.finished.connect(self.stop_thread)
        self.temp_file =temp_file
    @pyqtSlot()
    def run(self):
        self.player = QMediaPlayer()

        media = QMediaContent(QUrl.fromLocalFile(self.temp_file))
        self.player.setMedia(media)
        self.song_ready.emit()
        # Play the audio file

        self.player.play()
        try:
            while self.player.state() == QMediaPlayer.PlayingState:
                self.msleep(100)  # Sleep for 100 milliseconds
        except:
            pass

        self.stop_thread()

    def stop_thread(self):
        #print("stop_audio_called",self.temp_file)
        try:
            self.player.stop()
        except:
            pass
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.finished.emit()

class analysis_thread(QThread):
    def __init__(self,checking_thread,startMin,startSec,stopMin,stopSec):
        super().__init__()

    def run(self):
        test.asdf(to_display) # analysis function ,startMin,startSec,stopMin,stopSec)
        test.STOP = False # flag reset
        self.finished.emit()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.song_widget_list = []
        self.song_widget_recommend_list=[]
        self.ui = loadUi('.\\UI\\uiFiles\\Main.ui', self)
        self.setMinimumSize(1600, 900)
        self.mainStackedWidget = QStackedWidget(self)
        self.ui.widgetChange.layout().addWidget(self.mainStackedWidget)

        self.sideTabStackedWidget = QStackedWidget(self)
        self.sideTab.layout().addWidget(self.sideTabStackedWidget)
        #flags = self.windowFlags()
        #flags &= ~Qt.WindowMaximizeButtonHint
        #self.setWindowFlags(flags)

        self.SongListView = SongListView(self)
        self.RecommendListView = RecommendListView(self)
        self.Settings = Settings(self)

        self.NullSongInfo = loadUi(".\\UI\\uiFiles\\NullSongInfo.ui")
        self.NullSongInfo.label.setAlignment(Qt.AlignCenter)

        self.mainStackedWidget.addWidget(self.SongListView)
        self.mainStackedWidget.addWidget(self.RecommendListView)
        self.mainStackedWidget.addWidget(self.Settings)
        self.sideTabStackedWidget.addWidget(self.NullSongInfo)

        self._get_qss()

        self.ui.homeButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.SongListView))
        self.ui.recommendButton.clicked.connect(self.RecommendListView.change_widget)
        self.ui.recommendButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.RecommendListView))
        self.ui.settingButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.Settings))
        self.ui.homeButton.clicked.connect(self._home_selected)
        self.ui.recommendButton.clicked.connect(self._recommend_selected)
        self.ui.settingButton.clicked.connect(self._setting_selected)

        self.sideTabStackedWidget.setCurrentWidget(self.NullSongInfo)
        self.load()

        self.show()

    def load(self):
        folder_path = 'Datas'
        file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dat')]
        new_file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.tmpdat')]



        data = []
        new_data = []
        for file_path in new_file_list:
            with open(file_path, 'rb') as file:
                song_info = pickle.load(file)
                new_data.append(song_info)
            file.close()

        for filename in os.listdir(folder_path):
            if filename.endswith(".tmpdat"):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
        try:
            with open('./Datas/Addedlist.dat', 'rb') as f:
                song_info = pickle.load(f)
        except FileNotFoundError:
            song_info = []
        song_info += new_data
        with open('./Datas/Addedlist.dat', 'wb') as f:
            pickle.dump(song_info, f)

        for file_path in file_list:
            with open(file_path, 'rb') as file:
                song_info = pickle.load(file)
                data += song_info
            file.close()
        self.previous =None
        self.songlist = data

        for i in range(len(self.songlist)):
            song_widget_song = assets.SongFile(len(self.song_widget_list) + 1, self.songlist[i])
            song_widget_recommend = assets.SongFile(len(self.song_widget_list) + 1, self.songlist[i])
            self.SongListView.add_widget_in_song_list(song_widget_song)
            self.RecommendListView.add_widget_in_recommended_list(song_widget_recommend)

        del self.songlist
    def _get_qss(self):
        selected = QFile("UI/styleSheets/Selected.qss")
        not_selected = QFile("UI/styleSheets/NotSelected.qss")
        self.selected_style = ''
        self.not_selected_style = ''
        if selected.open(QFile.ReadOnly | QFile.Text):
            stream1 = QTextStream(selected)
            self.selected_style = stream1.readAll()
        if not_selected.open(QFile.ReadOnly | QFile.Text):
            stream2 = QTextStream(not_selected)
            self.not_selected_style = stream2.readAll()

    def show_sidetab(self, ToDisplay):
        del self.previous
        self.previous = self.sideTabStackedWidget.widget(0)
        self.sideTabStackedWidget.removeWidget(self.sideTabStackedWidget.widget(0))
        self.sideTabStackedWidget.addWidget(ToDisplay)
        self.sideTabStackedWidget.setCurrentWidget(ToDisplay)

    def _home_selected(self):
        self.ui.homeButton.setStyleSheet(self.selected_style)
        self.ui.recommendButton.setStyleSheet(self.not_selected_style)
        self.ui.settingButton.setStyleSheet(self.not_selected_style)

    def _recommend_selected(self):
        self.ui.homeButton.setStyleSheet(self.not_selected_style)
        self.ui.recommendButton.setStyleSheet(self.selected_style)
        self.ui.settingButton.setStyleSheet(self.not_selected_style)

    def _setting_selected(self):
        self.ui.homeButton.setStyleSheet(self.not_selected_style)
        self.ui.recommendButton.setStyleSheet(self.not_selected_style)
        self.ui.settingButton.setStyleSheet(self.selected_style)

    def disable_mainWidget(self):
        self.mainWidget.setEnabled(False)

    def enable_mainWidget(self):
        self.mainWidget.setEnabled(True)

    def disable_window(self):
        self.setEnabled(False)

    def enable_window(self):
        self.setEnabled(True)

    def _handle_song_file_click(self):
        song = self.sender()
        name = song.objectName()
        # below is tested code
        song_info_tab =SongInfo(song.root_file, self)
        self.show_sidetab(song_info_tab)

        public_functions.ratio(song_info_tab.ui.songInfoContainer, "Noto Sans KR medium", 0.15)
        public_functions.ratio(song_info_tab.ui.widget, "Noto Sans KR Black", 0.25)
        public_functions.ratio(song_info_tab.ui.DurationSet, "Noto Sans KR medium", 0.35)


class SongListView(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.to_display = mainui.song_widget_list
        self.init_ui(mainui)

    def init_ui(self, mainui):
        self.main = mainui
        self.analysis_process = None
        self.ui = loadUi(".\\UI\\uiFiles\\SongListView.ui")
        self.ui.AddSong.clicked.connect(self.start_input)
        self.layout = self.ui.contentsLayout
        self.ui.Search.textChanged.connect(self.search_in_whole_list)
        self._set_custom_scroll_bar()
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)
        self.name=''

        self.thread = Thread()
        self.thread.analysis_result_ready.connect(self.handle_analysis_result)

    def start_input(self):
        notification_window = assets.NotiFication("File format\n Artist-SongName.mp3\n 처음 시간이 조금 소요됩니다.", 3000,
                                                  self.main)  # Display the notification for 3000 milliseconds (3 seconds)
        notification_window.show()

        global input_file_directory
        input_file_directory = public_functions.open_file_dialog()

        self.thread.start()


    def handle_analysis_result(self, result):
        # Process the analysis result
        new_song = assets.SongFile(1, result)
        self.add_new_widget(new_song)
        # Re-enable the button
        notification_window = assets.NotiFication("New Song Uploaded", 3000,self.main)  # Display the notification for 3000 milliseconds (3 seconds)
        notification_window.show()

    def search_in_whole_list(self):
        self.name = self.ui.Search.text()
        self.to_display = public_functions.search(self.main.song_widget_list, self.name)

        # Hide all widgets
        for widget in self.main.song_widget_list:
            widget.hide()
            self.layout.removeWidget(widget)

            # Show widgets in search results
        for widget in self.to_display:
            widget.show()
            self.layout.addWidget(widget)

        self.update_index()

    def get_widget_number_from_song_list(self):
        return self.layout.count()


    def update_index(self):
        visible_widget_count = 0
        for index, widget in enumerate(self.to_display):
            visible_widget_count += 1
            widget.label0.setText(str(visible_widget_count))
            widget.update()

    def _reload_widgets(self):
        for widget in self.to_display:
            self.layout.removeWidget(widget)

            # Show widgets in search results
        for widget in self.to_display:
            self.layout.addWidget(widget)

    def _sort_widgets(self):
        self.main.song_widget_list.sort(key=lambda x: x.label1.text())
        self.to_display.sort(key=lambda x: x.label1.text())
        self._reload_widgets()
        self.update_index()

    def add_widget_in_song_list(self, song_widget):
        self.layout.addWidget(song_widget)
        song_widget.clicked.connect(self.main._handle_song_file_click)
        self.main.song_widget_list.append(song_widget)
        self._sort_widgets()
        self.layout.update()

    def add_new_widget(self, song_widget):
        global song_added
        self.main.song_widget_list = [song_widget] + self.main.song_widget_list
        self.main.song_widget_recommend_list = [song_widget] + self.main.song_widget_recommend_list
        if self.name in song_widget.label1.text():
            print(self.name, song_widget.label1.text())
            self.layout.insertWidget(0, song_widget)
            self.to_display = [song_widget] + self.to_display
        song_widget.clicked.connect(self.main._handle_song_file_click)
        song_added = True
        print(song_added)
        self._sort_widgets()
        self.layout.update()

    def _set_custom_scroll_bar(self):
        scroll_area = self.ui.songListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = assets.CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)


class RecommendListView(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\RecommendListView.ui")

        self.StackedWidget = self.ui.stackedWidget

        self.layout = self.ui.scrollAreaWidgetContents.layout()
        self.RecommendListScrollArea = self.ui.RecommendListScrollArea
        self.RecommendListScrollArea_widget = self.ui.RecommendListWidget

        self.make_profile_widget = self.ui.makeProfile
        self.Refresh_widget = self.ui.refresh
        public_functions.centering(self.make_profile_widget)
        self.ui.Search.textChanged.connect(self.search_in_recommended_list)
        self.ui.CanSing.clicked.connect(self.can_sing)
        self.ui.WellSing.clicked.connect(self.well_sing)
        self.ui.BarelySing.clicked.connect(self.barely_sing)
        self.StackedWidget.setCurrentWidget(self.make_profile_widget)
        self.displayed = self.main.song_widget_recommend_list
        self.searched = self.main.song_widget_recommend_list
        self._set_custom_scroll_bar()


        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def can_sing(self):
        can = can_sing()
        widgets = self.corresponding_widgets(can)
        self.displayed = widgets
        self.searched = widgets
        self._reload_widgets()

    def well_sing(self):
        well = well_sing()
        widgets = self.corresponding_widgets(well)
        self.displayed = widgets
        self.searched = widgets
        self._reload_widgets()
    def barely_sing(self):
        barely = can_sing()
        widgets = self.corresponding_widgets(barely)
        self.displayed = widgets
        self.searched = widgets
        self._reload_widgets()
    def corresponding_widgets(self,L=list):
        widgets = []
        for widget in self.main.song_widget_recommend_list:
            if widget.label1.text() in L:
                widgets.append(widget)
                L.remove(widget.label1.text())
        return widgets

    def search_in_recommended_list(self):
        name = self.ui.Search.text()
        self.searched= public_functions.search(self.displayed, name)

        # Hide all widgets
        for widget in self.displayed:
            widget.hide()
            self.layout.removeWidget(widget)

            # Show widgets in search results
        for widget in self.searched:
            widget.show()
            self.layout.addWidget(widget)

        self.update_index()

    def get_widget_number_from_recommended_list(self):
        return self.layout.count()

    def update_index(self):
        visible_widget_count = 0
        for index, widget in enumerate(self.searched):
            visible_widget_count += 1
            widget.label0.setText(str(visible_widget_count))
            widget.update()

    def add_widget_in_recommended_list(self, song_widget):
        self.layout.addWidget(song_widget)
        song_widget.clicked.connect(self.main._handle_song_file_click)
        self.main.song_widget_recommend_list.append(song_widget)
        self._sort_widgets()
        self.layout.update()

    def _reload_widgets(self):
        for widget in self.main.song_widget_recommend_list:
            self.layout.removeWidget(widget)
            widget.hide()
            # Show widgets in search results
        for widget in self.displayed:
            self.layout.addWidget(widget)
            widget.show()

    def _sort_widgets(self):
        self.main.song_widget_recommend_list.sort(key=lambda x: x.label1.text())
        self._reload_widgets()
        self.update_index()

    def change_widget(self):
        global song_added
        if not public_functions.profile_exist():
            self.StackedWidget.setCurrentWidget(self.make_profile_widget)
        elif song_added:
            self.StackedWidget.setCurrentWidget(self.Refresh_widget)
            self.displayed = self.main.song_widget_recommend_list
            self.searched = self.main.song_widget_recommend_list
            #song_added = False
        elif public_functions.profile_exist():
            self.StackedWidget.setCurrentWidget(self.RecommendListScrollArea_widget)

    def _set_custom_scroll_bar(self):
        scroll_area = self.ui.RecommendListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = assets.CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)

class SongInfo(QWidget):
    def __init__(self, song, mainui):
        super().__init__()

        self.song_name, self.artist, duration = song.name, song.artist, song.duration
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\SongInfo.ui")
        with open(f".\\additionalData\\{self.artist}-{self.song_name}\\adv.dat", 'rb') as file:
            AdvancedSongInfo = pickle.load(file)

        public_functions.centering(self.ui)

        self.ui.SongName.setText(self.song_name)
        self.ui.Artist.setText(self.artist)
        self.ui.Duration.setText(duration)
        self.ui.HighestNote.setText(str(AdvancedSongInfo.highest_note))
        self.ui.Expression.setText(str(AdvancedSongInfo.express))
        self.ui.SoundRange.setText(str(AdvancedSongInfo.note_range))
        self.ui.Breath.setText(str(AdvancedSongInfo.breath_hd))
        self.ui.Health.setText(str(AdvancedSongInfo.health))

        self.minuteDuration = int(duration[:2])
        self.secDuration = int(duration[3:])
        self.ui.StopMinuteValue.setMaximum(self.minuteDuration)

        self.ui.RecordButton.clicked.connect(self._handle_record_button_click)

        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)




    def resizeEvent(self, event):
        public_functions.ratio(self.ui.songInfoContainer,"Noto Sans KR medium", 0.15)
        public_functions.ratio(self.ui.widget, "Noto Sans KR Black", 0.25)
        public_functions.ratio(self.ui.DurationSet, "Noto Sans KR medium", 0.35)




    def _handle_record_button_click(self):
        startMin = self.ui.StartMinuteValue.value()
        startSec = self.ui.StartSecondValue.value()
        stopMin = self.ui.StopMinuteValue.value()
        stopSec = self.ui.StopSecondValue.value()

        if (stopMin * 60 + stopSec - startMin * 60 - startSec) < 15 or stopMin * 60 + stopSec > self.secDuration + self.minuteDuration * 60:
            return

        self.thread=RealTime(self,self.song_name,self.artist,startMin,startSec,stopMin,stopSec)
        self.record = RecordDisplay(self.main, self, self.song_name, self.artist)
        self.thread.start()
        self.main.show_sidetab(self.record)
        self.main.disable_mainWidget()


        # call scoring function


class RecordDisplay(QWidget):
    canceled = pyqtSignal(object)
    record_start =pyqtSignal()
    def __init__(self, mainui, songInfo,artist,songname):
        super().__init__()
        self.main = mainui
        self.songInfo = songInfo
        self.thread = self.songInfo.thread
        self.artist = artist
        self.songname  = songname
        self.ui = loadUi(".\\UI\\uiFiles\\Recording.ui")
        self.ui.CancelButton.clicked.connect(self._finished)
        self.ui.CancelButton.clicked.connect(self.canceled.emit)
        self.thread.display_new_info.connect(self.updateui)
        self.thread.start_timer.connect(self.start_timer)
        self.thread.finished.connect(self._finished)
        self.ui.Artist.setText(self.artist)
        self.ui.SongName.setText(self.songname)
        self.ui.Timer.setText("Loading...")
        public_functions.centering(self.ui)
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def _get_result(self):
        if live_analyis_result =="":
            QTimer.singleShot(100, self._get_result)
        else:
            return live_analyis_result
    def _finished(self):
        self.result = self._get_result()
        self._display_result()
    def _display_result(self):
        self.result = Result(self.main, self.songInfo, self.songname, self.artist)
        self.main.show_sidetab(self.result)

    def updateui(self,txts):
        self.ui.txt1.setText(txts[0])
        self.ui.txt2.setText(txts[1])

    def start_timer(self):
        self.ui.Timer.setText("3")
        QTimer.singleShot(1000, lambda: self.ui.Timer.setText("2"))
        QTimer.singleShot(2000, lambda: self.ui.Timer.setText("1"))
        QTimer.singleShot(3000, lambda: self.ui.Timer.setText("Start!"))
        QTimer.singleShot(3000, self.emit_record_start)
        QTimer.singleShot(4000, lambda: self.ui.Timer.setText("Recording"))

    def emit_record_start(self):
        self.record_start.emit()

class Settings(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.ui.resetButton.clicked.connect(self.main.disable_window)
        self.ui.resetButton.clicked.connect(lambda: public_functions.open_ok_or_cancel_dialog(self.main))
        self.ui.apply.clicked.connect(self.set_offset)
        self.offset = 0
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)
    def set_offset(self):
        self.offset = self.ui.offset.value()
        with open('.\\profile.dat', 'rb') as f:
            prf = pickle.load(f)

        prf.offset = self.offset

        with open('.\\profile.dat', 'wb') as f:
            pickle.dump(prf, f)


class Result(QWidget):
    def __init__(self, mainui,songInfo,songname,artist):
        super().__init__()
        self.main = mainui
        self.songInfo = songInfo
        self.artist = artist
        self.songname = songname
        self.ui = loadUi(".\\UI\\uiFiles\\Result.ui")
        public_functions.centering(self.ui)
        self.ui.BackButton.clicked.connect(self._handle_back_button_click)
        self.ui.SongName.setText(songname)
        self.ui.Artist.setText(artist)
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)
    def _handle_back_button_click(self):
        self.main.show_sidetab(self.songInfo)
        self.main.enable_mainWidget()






if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
