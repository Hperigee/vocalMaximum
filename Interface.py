from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from assets import SongFile, CustomScrollBar
from  SoundFormInfo import SoundFormInfo
import pickle
# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi('.\\UI\\uiFiles\\Main.ui', self)
        self.setMinimumSize(1600,900)
        self.mainStackedWidget = QStackedWidget(self)
        self.ui.widgetChange.layout().addWidget(self.mainStackedWidget)

        self.sideTabStackedWidget = QStackedWidget(self)
        self.sideTab.layout().addWidget(self.sideTabStackedWidget)


        self.SongListView=loadUi(".\\UI\\uiFiles\\SongListView.ui")
        self.RecommendListView = loadUi(".\\UI\\uiFiles\\RecommendListView.ui")
        self.Settings = loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.child_widget_1 = loadUi("child_widget_1.ui")
        self.NullSongInfo = loadUi(".\\UI\\uiFiles\\NullSongInfo.ui")

        self._set_custom_scroll_bar()

        self.mainStackedWidget.addWidget(self.SongListView)
        self.mainStackedWidget.addWidget(self.RecommendListView)
        self.mainStackedWidget.addWidget(self.Settings)
        self.mainStackedWidget.addWidget(self.child_widget_1)
        self.sideTabStackedWidget.addWidget(self.NullSongInfo)


        self.ui.homeButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.SongListView))
        self.ui.recommendButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.RecommendListView))
        self.ui.feedbackButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.child_widget_1))
        self.ui.settingButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.Settings))
        self.Settings.resetButton.clicked.connect(lambda: self.open_dialog(".\\UI\\uiFiles\\ResetConfirm.ui"))

        self.sideTabStackedWidget.setCurrentWidget(self.NullSongInfo)

        #below is testing
        example_song_1= SoundFormInfo("exampleSound", "artist1")

        song_widget = SongFile(self._get_widget_number_from_song_list()+1,example_song_1)

        song_widget.clicked.connect(self._handle_song_file_click)

        self._add_widget_in_song_list(song_widget)


        self.show()

    def open_dialog(self,uiName):
        # Create a new window
        new_window = NewDialog(uiName)
        # Show the new window and wait for user response
        result = new_window.exec_()
        if result==QDialog.Accepted:
            pass
            #implement reset code

    def _get_widget_number_from_song_list(self):
        return self.SongListView.contentsLayout.count()

    def _handle_song_file_click(self):
        song = self.sender()
        layout = self.SongListView.contentsLayout
        name=song.objectName()
        directory= name + '.dat'
        with open(directory, 'rb') as file:
           songInfo = pickle.load(file)

        file.close()

        self._show_song_info(songInfo)


    def _remove_widget_from_song_list(self, i):
        layout = self.SongListView.contentsLayout
        widget = self.SongListView.contentsLayout.itemAt(i).widget()
        layout.removeWidget(widget)
        widget.deleteLater()
        for j in range(i, self._get_widget_number_from_song_list()):
            change = self.SongListView.contentsLayout.itemAt(j).widget()
            change.label0.setText(str(j+1))
            change.update()

    def _add_widget_in_song_list(self,song_widget):
        layout = self.SongListView.contentsLayout
        layout.addWidget(song_widget)

    def _show_song_info(self,song):
        ToDisplay=self._make_song_info_display(song)
        self.sideTabStackedWidget.addWidget(ToDisplay)
        self.sideTabStackedWidget.setCurrentWidget(ToDisplay)


    def _set_custom_scroll_bar(self):
        scroll_area = self.SongListView.songListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)
    def _make_song_info_display(self, song):
        song_name, artist, duration = song.name, song.artist, song.duration

        songInfo = loadUi(".\\UI\\uiFiles\\SongInfo.ui")

        songInfo.SongName.setText(song_name)
        songInfo.Artist.setText(artist)
        songInfo.Duration.setText(duration)

        return songInfo



class NewDialog(QDialog):
    def __init__(self,uiName):
        super().__init__()
        self.ui = loadUi(uiName, self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.show()

app = QApplication([])

window = MainWindow()
app.exec_()

