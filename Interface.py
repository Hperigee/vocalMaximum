from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import uic

# Load the UI file
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main form created in Qt Designer
        self.ui = loadUi('.\\UI\\Main.ui', self)
        self.setMinimumSize(1280,720)
        # Create a stacked widget to hold the child widgets
        self.stacked_widget = QStackedWidget(self)
        self.ui.centralwidget.layout().addWidget(self.stacked_widget)

        # Load the child widgets from separate .ui files
        self.SongListView=uic.loadUi(".\\UI\\SongListView.ui")
        self.RecommendListView = uic.loadUi(".\\UI\\RecommendListView.ui")
        self.Settings = uic.loadUi(".\\UI\\Settings.ui")
        self.child_widget_1 = uic.loadUi("child_widget_1.ui")



        # Add the child widgets to the stacked widget
        self.stacked_widget.addWidget(self.SongListView)
        self.stacked_widget.addWidget(self.RecommendListView)
        self.stacked_widget.addWidget(self.Settings)
        self.stacked_widget.addWidget(self.child_widget_1)

        self.ui.Home_button.font().setPointSizeF(0.7*self.ui.Home_button.height())

        # Connect the sidebar buttons to switch between the child widgets
        self.ui.Home_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.SongListView))
        self.ui.Recommend_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.RecommendListView))
        self.ui.Feedback_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.child_widget_1))
        self.ui.Setting_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.Settings))
        self.Settings.Reset_button.clicked.connect(lambda: self.open_dialog(".\\UI\\ResetConfirm.ui"))
        for i in range(1000):
            song_widget = song_file(f"example{1000-i}", "00:00")
            song_widget.clicked.connect(self.handle_song_file_click)
            self.SongListView.Contents.layout().addWidget(song_widget)
        for i in range(1000,2):
            self.SongListView.Contents.removeWidget(song_widget)

        self.show()

    def open_dialog(self,uiName):
        # Create a new window
        new_window = NewDialog(uiName)
        # Show the new window and wait for user response
        result = new_window.exec_()
        if result==QDialog.Accepted:
            pass
        else:
            pass


    def handle_song_file_click(self):
        song = self.sender()
        print(f"{song.objectName()} was clicked.")
class song_file(QPushButton):
    def __init__(self,name, duration):
        super().__init__()
        self.setObjectName(name)
        self.label1 = QLabel(name)
        self.label2 = QLabel(duration)
        # Create the spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QHBoxLayout()

        # Add the labels and spacer to the layout
        layout.addWidget(self.label1)
        layout.addItem(spacer)
        layout.addWidget(self.label2)
        self.setLayout(layout)
        self.setFixedHeight(50)



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

