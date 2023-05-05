from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class song_file(QPushButton):
    def __init__(self, i, name, artist, duration):
        super().__init__()
        self.setFixedHeight(100)
        self.setObjectName(name)

        self.label0 = QLabel(str(i))
        self.label1 = QLabel(name)
        self.label2 = QLabel(artist)
        self.label3 = QLabel(duration)

        self.label0.setObjectName("index")
        self.label1.setObjectName("name")
        self.label2.setObjectName("artist")
        self.label3.setObjectName("duration")

        self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        filename = "UI/styleSheets/song_file.qss.qss"
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            style = stream.readAll()
        self.setStyleSheet(style)

        layout = QHBoxLayout()
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(30)
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)

        # Add the labels and spacer to the layout
        vlayout.addWidget(self.label1)
        vlayout.addWidget(self.label2)
        layout.addWidget(self.label0)
        layout.addLayout(vlayout)
        layout.addItem(spacer)
        layout.addWidget(self.label3)
        self.setLayout(layout)


class CustomScrollBar(QScrollBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the stylesheet to disable the default scrollbar
        filename = "UI/styleSheets/CustomScrollBar.qss"
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            style = stream.readAll()
        self.setStyleSheet(style)
