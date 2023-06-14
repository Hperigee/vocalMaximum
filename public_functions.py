import os
from PyQt5.QtWidgets import QFileDialog, QLabel, QDialog, QWidget,QSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi
from spleeter.separator import Separator
import pickle

class OkOrCancelDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi(".\\UI\\uiFiles\\ResetConfirm.ui", self)
        self.ui.buttonBox.accepted.connect(self.on_accepted)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.show()

    def on_accepted(self):
        # Code to be executed after the "accepted" button is clicked
        reset()
        self.accept()
def reset():

    with open('.\\profile.dat', 'rb') as f:
        prf = pickle.load(f)
    prf.can_max =0
    prf.well_max=0
    prf.verified_health=0
    prf.offset =0
    with open('.\\profile.dat', 'wb') as f:
        pickle.dump(prf, f)
    return



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
    with open('.\\profile.dat', 'rb') as f:
        prf = pickle.load(f)
    if prf.well_max == 0 and prf.can_max == 0 and prf.verified_health == 0:
        return False
    else: return True

def centering(widgets):
    for widget in widgets.findChildren(QLabel):
        widget.setAlignment(Qt.AlignCenter)

def ratio(widgets,font_str, ratio):
    for widget in widgets.findChildren(QWidget):
        widget_geometry = widget.geometry()
        font_size = widget_geometry.height() * ratio
        font = QFont(font_str, font_size)
        widget.setFont(font)
    for widget in widgets.findChildren(QSpinBox):
        widget_geometry = widget.geometry()
        font_size = widget_geometry.height() * ratio
        font = QFont(font_str, font_size)
        widget.setFont(font)

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