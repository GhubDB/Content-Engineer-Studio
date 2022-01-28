import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import * 
from excel_helpers import * 
from data import *
from stylesheets import *

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
        self.sidebar.selectionModel().selectionChanged.connect(self.detect_selected_cells)

        # Methods to be executed on startup
        self.populate_flows(example_flows)
        self.df = excel.load('sample.xlsx', 'Sheet1')
        excel.incomplete(self.df)
        self.populate_sidebar()

        # self.populate_sidebar(self)
        # self.actionOpen_Excel_File.pressed(excel.load())


    def populate_canned(self):
        '''
        Populates TableWidget of canned sentences
        '''
        self.canned.setColumnCount(2)
        self.canned.setRowCount(len(descriptors))
        for idx, row in enumerate(descriptors):
            self.canned.setItem(idx,0, QTableWidgetItem(row[0]))
            self.canned.setItem(idx,1, QTableWidgetItem(row[1]))
        # delegate = AlignDelegate(self.canned)
        # self.canned.setItemDelegateForColumn(1, delegate)
        self.canned.resizeColumnsToContents()
        self.canned.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def detect_selected_cells(self, selected, deselected):
        print(selected, deselected)
        for idx in selected.indexes():
            print(f'Selected Row: {idx.row()} Column: {idx.column()}')
        for idx in deselected.indexes():
            print(f'Deselected Row: {idx.row()} Column: {idx.column()}')



    def populate_sidebar(self):
        self.sidebar.setColumnCount(1)
        self.sidebar.setRowCount(len(self.df.index))
        for idx, row in self.df.iterrows():
            self.sidebar.setItem(idx,0, QTableWidgetItem(str(idx)))
            if row['bool_check'] == 1:
                self.sidebar.item(idx, 0).setBackground(QtGui.QColor(105, 79, 144))
            # else:
            #     self.sidebar.item(idx, 0).setBackground(QtGui.QColor(22, 41, 85))
        self.sidebar.resizeColumnsToContents()
        self.sidebar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  
    
    def populate_flows(self, flows):
        self.flows.setColumnCount(1)
        self.flows.setRowCount(len(flows))
        for idx, row in enumerate(flows):
            self.flows.setItem(idx,0, QTableWidgetItem(row))
        self.flows.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.flows.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
