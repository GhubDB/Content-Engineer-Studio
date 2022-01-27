import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import * 
from excel_helpers import * 
from data import *

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    '''
    For right alignment of QTableCells
    '''
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        loadUi('main_window.ui', self)
        self.setWindowTitle('CE Studio')
        
        # Connecting functions
        self.button.clicked.connect(self.populate_canned)

        # self.populate_sidebar(self)
        # self.actionOpen_Excel_File.pressed(excel.load())

    '''
    self.setWindowFlag(Qt.FramelessWindowHint)
    
    Use this to make the window title less and dragable
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)
    '''

        

    def populate_canned(self):
        '''
        Populates TableWidget of canned sentences
        '''
        self.canned.setColumnCount(2)
        self.canned.setRowCount(len(descriptors))
        for idx, row in enumerate(descriptors):
            # print(row[0])
            self.canned.setItem(idx,0, QTableWidgetItem(row[0]))
            self.canned.setItem(idx,1, QTableWidgetItem(row[1]))
        
        delegate = AlignDelegate(self.canned)
        self.canned.setItemDelegateForColumn(1, delegate)
        self.canned.resizeColumnsToContents()

    def populate_sidebar(self, *df):
        self.sidebar.setRowCount(len(df.index))
        for i, row in df.iterrows():
            if row['bool_check'] == 1:
                pass
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())
