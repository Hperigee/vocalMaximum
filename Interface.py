from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFile, QTextStream, QTimer
from Resources_rc import *
import pickle
import os
import public_functions
import assets
import multiprocessing
from queue import Empty
from fileinput import input_file
import time
import sys



# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.song_widget_list = []
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
        self.songlist = data[0]


        for i in range(len(self.songlist)):
            song_widget = assets.SongFile(len(self.song_widget_list) + 1, self.songlist[i])
            song_widget.clicked.connect(self._handle_song_file_click)
            self.SongListView.add_widget_in_song_list(song_widget)

        del self.songlist


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

    def _handle_song_file_click(self):
        song = self.sender()
        name = song.objectName()
        # below is tested code
        self.show_sidetab(SongInfo(song.root_file, self))


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


    def start_input(self):
        notification_window = assets.NotiFication("File format\n Artist-SongName.mp3", 3000,
                                                  self.main)  # Display the notification for 3000 milliseconds (3 seconds)
        notification_window.show()

        directory = public_functions.open_file_dialog()

        self.analysis_process = multiprocessing.Process(target=input_worker, args=(directory,result_queue,))
        self.analysis_process.start()


        QTimer.singleShot(1500, check_result_queue)



    def handle_analysis_result(self, result):
        # Process the analysis result
        new_song = assets.SongFile(1, result)
        self.add_new_widget(new_song)
        # Re-enable the button
        notification_window = assets.NotiFication("New Song Uploaded", 3000,self.main)  # Display the notification for 3000 milliseconds (3 seconds)
        notification_window.show()

    def search_in_whole_list(self):
        name = self.ui.Search.text()
        self.to_display = public_functions.search(self.main.song_widget_list, name)

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

    def remove_widget_from_song_list(self, i):
        widget = self.layout.itemAt(i).widget()
        self.layout.removeWidget(widget)
        self.update_index()

    def update_index(self):
        visible_widget_count = 0
        for index, widget in enumerate(self.to_display):
            visible_widget_count += 1
            widget.label0.setText(str(visible_widget_count))
            widget.update()

    def add_widget_in_song_list(self, song_widget):
        self.layout.addWidget(song_widget)
        song_widget.clicked.connect(self.main._handle_song_file_click)
        self.main.song_widget_list.append(song_widget)
        self.layout.update()

    def add_new_widget(self,song_widget):
        self.layout.insertWidget(0, song_widget)
        self.main.song_widget_list=[song_widget]+self.main.song_widget_list
        self.to_display = [song_widget] + self.to_display
        song_widget.clicked.connect(self.main._handle_song_file_click)
        self.layout.update()
        self.update_index()

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
        with open(f".\\additionalData\\{artist}-{song_name}\\adv.dat", 'rb') as file:
            AdvancedSongInfo = pickle.load(file)

        public_functions.centering(self.ui)

        self.ui.SongName.setText(song_name)
        self.ui.Artist.setText(artist)
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
        self.ui.Search.textChanged.connect(self.search_in_recommended_list)
        self.StackedWidget.setCurrentWidget(self.make_profile_widget)

        self._set_custom_scroll_bar()

        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)

    def search_in_recommended_list(self):
        name = self.ui.Search.text()
        L = []  # it will be recommended list
        to_display = public_functions.search(L, name)
        self.remove_whole_list()
        for i in range(len(to_display)):
            self.add_widget_in_recommend_list(to_display[i])

    def remove_whole_list(self):
        for x in range(self.get_widget_number_from_recommend_list()):
            widget = self.layout.itemAt(0).widget()
            self.layout.removeWidget(widget)

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

    def add_widget_in_recommend_list(self, song_widget):
        self.layout.addWidget(song_widget)
        self.layout.update()

    def _set_custom_scroll_bar(self):
        scroll_area = self.RecommendListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = assets.CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)


class Settings(QWidget):
    def __init__(self, mainui):
        super().__init__()
        self.main = mainui
        self.ui = loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.ui.resetButton.clicked.connect(self.main.disable_window)
        self.ui.resetButton.clicked.connect(lambda: public_functions.open_ok_or_cancel_dialog(self.main))
        display = QHBoxLayout()
        display.setContentsMargins(0, 0, 0, 0)
        display.addWidget(self.ui)
        self.setLayout(display)


def input_worker(directory,result_queue):
    if directory!= None:
        result = input_file(directory)
        result_queue.put(result)

def check_result_queue():
    try:
        while True:
            result= result_queue.get(block=False)
            window.SongListView.handle_analysis_result(result)
    except Empty:
        pass
    if window.SongListView.analysis_process and window.SongListView.analysis_process.is_alive():
        # Schedule the next check after a delay
        QTimer.singleShot(2000, check_result_queue)




if __name__ == "__main__":
    import time
    app = QApplication([])
    window = MainWindow()
    window.show()
    result_queue=multiprocessing.Queue()
    app.exec_()
