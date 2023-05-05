from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import uic
from assets import song_file, CustomScrollBar
import Resources_rc

# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi('.\\UI\\uiFiles\\Main.ui', self)
        self.setMinimumSize(1600,900)
        self.mainStackedWidget = QStackedWidget(self)
        self.ui.widgetChange.layout().addWidget(self.mainStackedWidget)


        self.SongListView=uic.loadUi(".\\UI\\uiFiles\\SongListView.ui")
        self.RecommendListView = uic.loadUi(".\\UI\\uiFiles\\RecommendListView.ui")
        self.Settings = uic.loadUi(".\\UI\\uiFiles\\Settings.ui")
        self.child_widget_1 = uic.loadUi("child_widget_1.ui")

        self._set_custom_scroll_bar()

        self.mainStackedWidget.addWidget(self.SongListView)
        self.mainStackedWidget.addWidget(self.RecommendListView)
        self.mainStackedWidget.addWidget(self.Settings)
        self.mainStackedWidget.addWidget(self.child_widget_1)


        self.ui.homeButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.SongListView))
        self.ui.recommendButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.RecommendListView))
        self.ui.feedbackButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.child_widget_1))
        self.ui.settingButton.clicked.connect(lambda: self.mainStackedWidget.setCurrentWidget(self.Settings))
        self.Settings.resetButton.clicked.connect(lambda: self.open_dialog(".\\UI\\uiFiles\\ResetConfirm.ui"))


        for i in range(1000):
            song_widget = song_file(self._get_widget_number_from_song_list()+1,f"example{i}", f"exampleartist{i}","00:00")
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
        print(f"{song.objectName()} is removed.")
        self._remove_widget_from_song_list(layout.indexOf(song))

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

    def show_song_info(self):
        pass


    def _set_custom_scroll_bar(self):
        scroll_area = self.SongListView.songListScrollArea
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        custom_scrollbar = CustomScrollBar()
        scroll_area.setVerticalScrollBar(custom_scrollbar)





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

