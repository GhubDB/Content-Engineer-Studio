import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtWidgets import * 
from excel_helpers import * 
from data import *
from stylesheets import *

class TextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.updateGeometry)

    def sizeHint(self):
        hint = super().sizeHint()
        if self.toPlainText():
            doc = self.document().clone()
            width = self.width() - self.frameWidth() * 2
            if self.verticalScrollBar().isVisible():
                width -= self.verticalScrollBar().width()
            doc.setTextWidth(width)
            height = round(doc.size().height())
        else:
            height = self.fontMetrics().height()
            height += self.document().documentMargin() * 2
        height += self.frameWidth() * 2
        hint.setHeight(height)
        return hint


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("MyApp.ui", self)
        self.tableWidget_3.verticalHeader().setVisible(False)
        self.tableWidget_3.horizontalHeader().setVisible(False)
        self.tableWidget_3.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)

        for i in range(10):
            rowCount = self.tableWidget_3.rowCount()
            self.tableWidget_3.insertRow(rowCount)
            combo = TextEdit(self)
            self.tableWidget_3.setCellWidget(i, 0, combo)
            combo.setText(text)
            combo.textChanged.connect(
                lambda i=i: self.tableWidget_3.resizeRowToContents(i))
        self.tableWidget_3.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == event.Resize:
            QTimer.singleShot(0, self.tableWidget_3.resizeRowsToContents)
        return super().eventFilter(source, event)

MyApp()