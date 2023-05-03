import sys
from PyQt5 import uic, QtWidgets

# Load the UI file
qtCreatorFile = ".\\UI\\Main.ui"  # Your UI file name
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Add a widget to the scroll area
class Songdata(QtWidgets.QWidget):
    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    widget_list = []

    for i in range(100):
        label = QtWidgets.QLabel(f"Label {i}")
        window.Contents.layout().addWidget(label)

    sys.exit(app.exec_())
