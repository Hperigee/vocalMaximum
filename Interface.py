from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFile, QTextStream
from Resources_rc import *
import pickle
import os
import public_functions
import assets


# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi('.\\UI\\uiFiles\\Main.ui', self)
        self.setMinimumSize(1600, 900)
        self.mainStackedWidget = QStackedWidget(self)
        self.ui.widgetChange.layout().addWidget(self.mainStackedWidget)

        self.sideTabStackedWidget = QStackedWidget(self)
        self.sideTab.layout().addWidget(self.sideTabStackedWidget)

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

        self.previous = None

        self.ui.homeButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.SongListView))
        self.ui.recommendButton.clicked.connect(self.RecommendListView.change_widget)
        self.ui.recommendButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.RecommendListView))
        self.ui.settingButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.Settings))
        self.ui.homeButton.clicked.connect(self._home_selected)
        self.ui.recommendButton.clicked.connect(self._recommend_selected)
        self.ui.settingButton.clicked.connect(self._setting_selected)

        self.sideTabStackedWidget.setCurrentWidget(self.NullSongInfo)

        # below is tested code
        folder_path = '.\\testData'
        file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dat')]
        data = []
        for file_path in file_list:
            with open(file_path, 'rb') as file:
                songInfo = pickle.load(file)
                data.append(songInfo)
            file.close()

        for i in range(len(data)):
            self.SongListView.add_widget_in_song_list(data[i])
        for i in range(0, len(data), 2):
            self.RecommendListView.add_widget_in_recommend_list(data[i])
        del data

        self.show()

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


class SongListView(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\SongListView.ui")
        self.ui.AddSong.clicked.connect(public_functions.open_file_dialog)
        self.layout = self.ui.contentsLayout
        self._set_custom_scroll_bar()
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def get_widget_number_from_song_list(self):
        return self.layout.count()

    def remove_widget_from_song_list(self, i):
        widget = self.layout.itemAt(i).widget()
        self.layout.removeWidget(widget)
        widget.deleteLater()
        for j in range(i, self.get_widget_number_from_song_list()):
            change = self.layout.itemAt(j).widget()
            change.label0.setText(str(j + 1))
            change.update()

    def add_widget_in_song_list(self, song_file):
        song_widget = assets.SongFile(self.get_widget_number_from_song_list() + 1, song_file)
        song_widget.clicked.connect(self._handle_song_file_click)
        self.layout.addWidget(song_widget)
        self.layout.update()

    def _handle_song_file_click(self):
        song = self.sender()
        name = song.objectName()
        # below is tested code
        directory = f'.\\testData\\{name}.dat'

        with open(directory, 'rb') as file:
            song_info = pickle.load(file)
        file.close()
        self.main.show_sidetab(SongInfo(song_info, self.main))

    def _set_custom_scroll_bar(self):
        scroll_area = self.ui.songListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = assets.CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)


class SongInfo(QWidget):
    def __init__(self, song, mainui):
        super().__init__()

        song_name, artist, duration = song.name, song.artist, song.duration
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\SongInfo.ui")

        public_functions.centering(self.ui)

        self.ui.SongName.setText(song_name)
        self.ui.Artist.setText(artist)
        self.ui.Duration.setText(duration)
        self.minuteDuration = int(duration[:2])
        self.secDuration = int(duration[3:])
        self.ui.StopMinuteValue.setMaximum(self.minuteDuration)

        self.ui.RecordButton.clicked.connect(self._handle_record_button_click)
        self.ui.UploadButton.clicked.connect(public_functions.open_file_dialog)

        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def _handle_record_button_click(self):
        startMin = self.ui.StartMinuteValue.value()
        startSec = self.ui.StartSecondValue.value()
        stopMin = self.ui.StopMinuteValue.value()
        stopSec = self.ui.StopSecondValue.value()

        if stopMin * 60 + stopSec - startMin * 60 + startSec < 15 or stopMin * 60 + stopSec > self.secDuration + self.minuteDuration * 60:
            return

        self.main.show_sidetab(RecordDisplay(self.main))
        self.main.disable_mainWidget()

        # call scoring function


class RecordDisplay(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\Recording.ui")
        self.ui.CancelButton.clicked.connect(self._handle_record_cancel_button_click)
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def _handle_record_cancel_button_click(self):
        self.main.show_sidetab(self.main.previous)
        self.main.enable_mainWidget()


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
        public_functions.centering(self.make_profile_widget)

        self.StackedWidget.setCurrentWidget(self.make_profile_widget)

        self._set_custom_scroll_bar()

        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def change_widget(self):
        if public_functions.profile_exist():
            self.StackedWidget.setCurrentWidget(self.RecommendListScrollArea_widget)

    def get_widget_number_from_recommend_list(self):
        return self.layout.count()

    def remove_widget_from_recommend_list(self, i):
        widget = self.layout.itemAt(i).widget()
        self.layout.removeWidget(widget)
        widget.deleteLater()
        for j in range(i, self.get_widget_number_from_recommend_list()):
            change = self.layout.itemAt(j).widget()
            change.label0.setText(str(j + 1))
            change.update()

    def add_widget_in_recommend_list(self, song_file):
        song_widget = assets.SongFile(self.get_widget_number_from_recommend_list() + 1, song_file)
        song_widget.clicked.connect(self._handle_song_file_click)

        self.layout.addWidget(song_widget)
        self.layout.update()

    def _handle_song_file_click(self):
        song = self.sender()
        name = song.objectName()
        # below is tested code
        directory = f'.\\testData\\{name}.dat'

        with open(directory, 'rb') as file:
            song_info = pickle.load(file)
        file.close()
        self.main.show_sidetab(SongInfo(song_info, self.main))

    def _set_custom_scroll_bar(self):
        scroll_area = self.RecommendListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = assets.CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)


class Settings(QWidget):
    def __init__(self, mainui):

        super().__init__()
        self.main=mainui
        self.ui = loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.ui.resetButton.clicked.connect(self.main.disable_window)
        self.ui.resetButton.clicked.connect(lambda: public_functions.open_ok_or_cancel_dialog(self.main))
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)
