from PyQt5.QtWidgets import QFileDialog, QLabel, QDialog
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class OkOrCancelDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi(".\\UI\\uiFiles\\ResetConfirm.ui", self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.show()


def profile_exist():
    return False

def open_file_dialog():
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Open File")
    if file_path:
        print("Selected file:", file_path)


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

def search(L,name): #L is list of SoundFormInfo
    M=[]
    for x in L:
        if name in x.name:
            M.append(x)
    return M
