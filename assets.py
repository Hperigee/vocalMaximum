from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFile, QTextStream, QTimer,Qt
from PyQt5.uic import loadUi
import public_functions

class NotiFication(QMainWindow):
    def __init__(self,text,duration,main):
        super().__init__()
        self.main=main
        self.duration = duration
        self.text = text

        self.init_ui()


    def init_ui(self):
        self.ui = loadUi(".\\UI\\uiFiles\\Notification.ui",self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.ui.message.setText(self.text)
        self.ui.message.setStyleSheet("""
                                        background-color:rgb(7, 3, 122);
                                        color: white;
                                        """)
        public_functions.centering(self.ui)

        # Calculate the position of the window
        parent_geometry = self.main.geometry()

        # Calculate the position of the window
        window_width = self.geometry().width()
        window_height = self.geometry().height()
        x = parent_geometry.right() - window_width
        y = parent_geometry.bottom() - window_height

        # Set the position of the window
        self.move(x, y)
        # Start the timer to close the window after the specified duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.close_window)
        self.timer.start(self.duration)

        self.show()
    def close_window(self):
        self.timer.stop()
        self.close()

class SongFile(QPushButton):
    def __init__(self, i, song):

        super().__init__()
        self.setFixedHeight(80)
        name, artist, duration = song.name, song.artist, song.duration
        self.root_file=song
        self.setObjectName(name)
        self.label0 = QLabel(str(i))
        self.label1 = QLabel(name)
        self.label2 = QLabel(artist)
        self.label3 = QLabel(duration)

        self.label0.setObjectName("index")
        self.label1.setObjectName("name")
        self.label2.setObjectName("artist")
        self.label3.setObjectName("duration")
        self.label0.setFixedWidth(50)

        self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        public_functions.centering(self.label0)
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        filename = "UI/styleSheets/SongFile.qss"
        file = QFile(filename)
        style = ''
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            style = stream.readAll()
        self.setStyleSheet(style)

        layout = QHBoxLayout()
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(10)
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)

        # Add the labels and spacer to the layout

        vlayout.addWidget(self.label1)
        vlayout.addWidget(self.label2)
        layout.addWidget(self.label0)
        layout.addLayout(vlayout)
        layout.addItem(spacer2)
        layout.addWidget(self.label3)
        self.setLayout(layout)

class CustomScrollBar(QScrollBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the stylesheet to disable the default scrollbar
        filename = "UI/styleSheets/CustomScrollBar.qss"
        file = QFile(filename)
        style = ''
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            style = stream.readAll()

        self.setStyleSheet(style)




