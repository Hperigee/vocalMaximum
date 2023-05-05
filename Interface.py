from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from assets import SongFile, CustomScrollBar
from SoundFormInfo import SoundFormInfo
import pickle
import os

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

        self.SongListView = loadUi(".\\UI\\uiFiles\\SongListView.ui")
        self.RecommendListView = loadUi(".\\UI\\uiFiles\\RecommendListView.ui")
        self.Settings = loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.NullSongInfo = loadUi(".\\UI\\uiFiles\\NullSongInfo.ui")

        self._set_custom_scroll_bar()

        self.mainStackedWidget.addWidget(self.SongListView)
        self.mainStackedWidget.addWidget(self.RecommendListView)
        self.mainStackedWidget.addWidget(self.Settings)
        self.sideTabStackedWidget.addWidget(self.NullSongInfo)

        self.previous = None

        self.ui.homeButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.SongListView))
        self.ui.recommendButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.RecommendListView))
        self.ui.settingButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.Settings))
        self.Settings.resetButton.clicked.connect(lambda: self.open_dialog(".\\UI\\uiFiles\\ResetConfirm.ui"))

        self.sideTabStackedWidget.setCurrentWidget(self.NullSongInfo)

        # below is test code
        folder_path = '.\\testData'
        file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dat')]
        data = []
        for file_path in file_list:
            with open(file_path, 'rb') as file:
                songInfo = pickle.load(file)
                data.append(songInfo)
            file.close()

        for datum in data:
            song_widget = SongFile(self._get_widget_number_from_song_list() + 1, datum)
            song_widget.clicked.connect(self._handle_song_file_click)
            self._add_widget_in_song_list(song_widget)

        del data

        self.show()

    def open_dialog(self, uiName):
        # Create a new window
        new_window = NewDialog(uiName)
        # Show the new window and wait for user response
        result = new_window.exec_()
        if result == QDialog.Accepted:
            pass
            # implement reset code

    def _get_widget_number_from_song_list(self):
        return self.SongListView.contentsLayout.count()

    def _handle_song_file_click(self):
        song = self.sender()
        name = song.objectName()
        # below is test code
        directory = f'.\\testData\\{name}.dat'

        with open(directory, 'rb') as file:
            songInfo = pickle.load(file)
        file.close()

        self._show_sidetab(self._make_song_info_display(songInfo))

    def _handle_record_button_click(self):

        startMin = self.songInfo.StartMinuteValue.value()
        startSec = self.songInfo.StartSecondValue.value()
        stopMin = self.songInfo.StopMinuteValue.value()
        stopSec = self.songInfo.StopSecondValue.value()

        self._show_sidetab(self._make_record_display())
        self._disable_songlist()

        # call scoring function

    def _handle_record_cancel_button_click(self):
        song = self.sender()
        startMin = self.songInfo.StartMinuteValue.value()
        startSec = self.songInfo.StartSecondValue.value()
        stopMin = self.songInfo.StopMinuteValue.value()
        stopSec = self.songInfo.StopSecondValue.value()

        self._show_sidetab(self.previous)
        self._enable_songlist()

        # call scoring function

    def _remove_widget_from_song_list(self, i):
        layout = self.SongListView.contentsLayout
        widget = self.SongListView.contentsLayout.itemAt(i).widget()
        layout.removeWidget(widget)
        widget.deleteLater()
        for j in range(i, self._get_widget_number_from_song_list()):
            change = self.SongListView.contentsLayout.itemAt(j).widget()
            change.label0.setText(str(j + 1))
            change.update()

    def _add_widget_in_song_list(self, song_widget):
        layout = self.SongListView.contentsLayout
        layout.addWidget(song_widget)

    def _show_sidetab(self, ToDisplay):
        del self.previous
        self.previous = self.sideTabStackedWidget.widget(0)
        self.sideTabStackedWidget.removeWidget(self.sideTabStackedWidget.widget(0))
        self.sideTabStackedWidget.addWidget(ToDisplay)
        self.sideTabStackedWidget.setCurrentWidget(ToDisplay)

    def _set_custom_scroll_bar(self):
        scroll_area = self.SongListView.songListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)

    def _make_song_info_display(self, song):
        song_name, artist, duration = song.name, song.artist, song.duration

        self.songInfo = loadUi(".\\UI\\uiFiles\\SongInfo.ui")

        self.songInfo.SongName.setText(song_name)
        self.songInfo.Artist.setText(artist)
        self.songInfo.Duration.setText(duration)
        self.songInfo.StopMinuteValue.setMaximum(int(duration[:2]))

        self.songInfo.RecordButton.clicked.connect(self._handle_record_button_click)

        return self.songInfo

    def _make_record_display(self):
        self.record_display = loadUi(".\\UI\\uiFiles\\Recording.ui")
        self.record_display.CancelButton.clicked.connect(self._handle_record_cancel_button_click)
        return self.record_display

    def _disable_songlist(self):
        widgets = self.SongListView.contents
        for widget in widgets.findChildren(QPushButton):
            widget.setEnabled(False)

    def _enable_songlist(self):
        widgets = self.SongListView.contents
        for widget in widgets.findChildren(QPushButton):
            widget.setEnabled(True)


class NewDialog(QDialog):
    def __init__(self, uiName):
        super().__init__()
        self.ui = loadUi(uiName, self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.show()


def _profile_exist():
    return False
