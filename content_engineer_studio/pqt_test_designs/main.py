import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QApplication
from utils.excel_helpers import *


class MainWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(*args, **kwargs)

        loadUi("ce_studio.ui", self)
        self.setWindowTitle("CE Studio")

    def canned(self):
        self.canned.setRowCount(6)
        self.canned.setColumnCount(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())
