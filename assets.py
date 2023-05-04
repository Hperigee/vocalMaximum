from PyQt5.QtWidgets import *


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
        # Create the spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(30)
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)
        self.setStyleSheet('''
                    QPushButton {
                        background-color: #eeeeee;
                        border-radius: 35px;
                        }

                    QPushButton:hover {
                        background-color: #bbbbbb;
                        }

                    QPushButton:pressed {
                        background-color: #999999;
                        padding-top: 15px;
                        padding-bottom: 5px;
                        }

                    QLabel#index{
                    background-color: transparent;
                    font: 12pt "Noto Sans KR medium";
                    color:#444444;
                    }

                    QLabel#name{
                    background-color: transparent;
                    font: 14pt "Noto Sans KR medium";
                    color:black;
                    }

                    QLabel#artist{
                    background-color:transparent;
                    font: 10pt "Noto Sans KR";
                    color:#444444;
                    }

                    QLabel#duration{
                    background-color:transparent;
                    font: 12pt "Noto Sans KR";
                    color:#444444;
                    }

                    ''')

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
        self.setStyleSheet('''
                            QScrollBar:vertical {
                                background: transparent;
                                width: 60px;
                                margin: 30px 20px 30px 20px;
                                border: none;
                            }

                            QScrollBar::handle:vertical {
                                background: #666;
                                min-height: 80px;

                                margin: 0px 0px 0px 0px;
                                border-radius: 10px;
                            }
                            QScrollBar::handle:vertical:hover {
                                background: #444;

                            }

                            QScrollBar::add-line:vertical {
                                background: #f1f1f1;
                                height: 0px;
                                subcontrol-position: bottom;
                                subcontrol-origin: margin;
                            }

                            QScrollBar::sub-line:vertical {
                                background: #f1f1f1;
                                height: 0px;
                                subcontrol-position: top;
                                subcontrol-origin: margin;
                            }

                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                background: none;
                            }

                        ''')



