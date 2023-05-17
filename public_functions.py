from PyQt5.QtWidgets import QFileDialog, QLabel, QDialog, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from spleeter.separator import Separator

class OkOrCancelDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi(".\\UI\\uiFiles\\ResetConfirm.ui", self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.show()


from PyQt5.QtWidgets import QFileDialog

def open_file_dialog():
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("MP3 Files (*.mp3)")

    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        # Filter selected files to keep only .mp3 files
        selected_files = [file for file in selected_files if file.endswith('.mp3')]
        return selected_files
    else:
        return None



def profile_exist():
    return True


def centering(widgets):
    for widget in widgets.findChildren(QLabel):
        widget.setAlignment(Qt.AlignCenter)


def open_ok_or_cancel_dialog(mainui):
    # Show the new window and wait for user response
    new_window = OkOrCancelDialog()
    result = new_window.exec_()
    if result == QDialog.Accepted:
        pass
    mainui.enable_window()
        # implement reset code

def search(L, name):
    M = [x for x in L if name in x.root_file.name]
    return M

def separate(directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(directory, './temp')
    return