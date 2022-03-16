from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal


class CustomTextEdit(QtWidgets.QTextEdit):
    def __init_subclass__(self) -> None:
        return super().__init_subclass__()
