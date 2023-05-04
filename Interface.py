from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import uic
from assets import song_file, CustomScrollBar

# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = loadUi('.\\UI\\Main.ui', self)
        self.setMinimumSize(1280,720)
        self.main_stacked_widget = QStackedWidget(self)
        self.ui.widgetChange.layout().addWidget(self.main_stacked_widget)


        self.SongListView=uic.loadUi(".\\UI\\SongListView.ui")
        self.RecommendListView = uic.loadUi(".\\UI\\RecommendListView.ui")
        self.Settings = uic.loadUi(".\\UI\\Settings.ui")
        self.child_widget_1 = uic.loadUi("child_widget_1.ui")

        self.set_custom_scroll_bar()

        self.main_stacked_widget.addWidget(self.SongListView)
        self.main_stacked_widget.addWidget(self.RecommendListView)
        self.main_stacked_widget.addWidget(self.Settings)
        self.main_stacked_widget.addWidget(self.child_widget_1)


        self.ui.Home_button.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.SongListView))
        self.ui.Recommend_button.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.RecommendListView))
        self.ui.Feedback_button.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.child_widget_1))
        self.ui.Setting_button.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.Settings))
        self.Settings.Reset_button.clicked.connect(lambda: self.open_dialog(".\\UI\\ResetConfirm.ui"))

        song_widget_list=[]
        for i in range(1000):
            song_widget = song_file(self.get_widget_number_from_list()+1,f"example{i}", f"exampleartist{i}","00:00")
            song_widget.clicked.connect(self.handle_song_file_click)
            song_widget_list.append(song_widget)
            self.add_widget_in_list(song_widget)

        deleted=self.remove_widget_from_list(2,song_widget_list)
        self.SongListView.Contents.layout().addWidget(deleted)

        self.show()

    def open_dialog(self,uiName):
        # Create a new window
        new_window = NewDialog(uiName)
        # Show the new window and wait for user response
        result = new_window.exec_()
        if result==QDialog.Accepted:
            pass
            #implement reset code

    def get_widget_number_from_list(self):
        return self.SongListView.Contents_Layout.count()

    def remove_widget_from_list(self,i,L):
        widget1 = self.SongListView.Contents.layout().itemAt(i).widget()
        self.SongListView.Contents.layout().removeWidget(widget1)
        L.pop(i)
        return widget1
    def add_widget_in_list(self,song_widget):
        self.SongListView.Contents.layout().addWidget(song_widget)

    def show_songInfo(self):
        pass
    def handle_song_file_click(self):
        song = self.sender()
        print(f"{song.objectName()} was clicked.")

    def set_custom_scroll_bar(self):
        scroll_area = self.SongListView.Songlist_scrollArea
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

