import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import * 
from excel_helpers import * 
from data import *
from stylesheets import *

class TextEdit(QTextEdit):
    '''
    Text edits in tables
    '''
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


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.row = 0
        self.header_len = 0
        self.index_len = 0

        # Sets the starting column number for the cell selector combo box
        self.cell_selector_start = 4

        loadUi('main_window.ui', self)
        self.setWindowTitle('CE Studio')
        
        # Connecting functions
        self.sidebar.selectionModel().selectionChanged.connect(self.row_selector)
        self.cell_selector.currentIndexChanged.connect(self.populate_analysis)
        self.analysis.textChanged.connect(self.save_analysis)
        self.left.clicked.connect(self.btn_left)
        self.right.clicked.connect(self.btn_right)

        # Methods to be executed on startup
        self.populate_canned()
        

        self.populate_flows(example_flows)
        self.populate_actions(example_actions)
        self.df = excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        excel.incomplete(self.df)
        self.populate_sidebar()
        self.populate_status_bar(2, 0, 2)
        self.populate_cell_selector(self.cell_selector_start, -1)
        self.populate_chat()

        # Tests
        print(xw.books.active.name)
        # print(self.df.head)


    def eventFilter(self, source, event):
        '''
        Intercepts resize events for the table widget
        '''
        if event.type() == event.Resize:
            QTimer.singleShot(0, self.tableWidget_3.resizeRowsToContents)
        return super().eventFilter(source, event)


    def row_selector(self, selected):
        '''
        Keeps the current row number updated
        '''
        idx = selected.indexes()
        self.row = idx[0].row()

    def save_analysis(self):
        '''
        Saves current analysis text to dataframe
        '''
        self.df.loc[self.row][self.cell_selector.currentText()] = self.analysis.toPlainText()
    
    def populate_chat(self):
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(example_chat))
        for idx, message in enumerate(example_chat):
            self.chat.setItem(idx,0, QTableWidgetItem(message))
            # if idx % 2 == 0:
            #     self.chat.item(idx, 0).setBackground(QtGui.QColor(212, 177, 106))
            # else:
            #     self.chat.item(idx, 0).setBackground(QtGui.QColor(120, 135, 171))
        self.chat.resizeColumnsToContents()
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def populate_analysis(self, signal):
        self.analysis.setText(self.df.loc[self.row][signal+self.cell_selector_start])

    def populate_cell_selector(self, start, end):
        for item in list(self.df.columns.values)[start:end]:
            self.cell_selector.addItem(item)

    def populate_canned(self):
        '''
        Populates TableWidget of canned sentences
        '''
        self.canned.setColumnCount(2)
        self.canned.setRowCount(len(descriptors))
        for idx, row in enumerate(descriptors):
            self.canned.setItem(idx,0, QTableWidgetItem(row[0]))
            self.canned.setItem(idx,1, QTableWidgetItem(row[1]))
        self.canned.resizeColumnsToContents()
        self.canned.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def populate_sidebar(self):
        self.sidebar.setColumnCount(1)
        self.sidebar.setRowCount(len(self.df.index))
        for idx, row in self.df.iterrows():
            self.sidebar.setItem(idx,0, QTableWidgetItem(str(idx + 1)))
            if row['bool_check'] == 1:
                self.sidebar.item(idx, 0).setBackground(QtGui.QColor(105, 79, 144))
            # else:
            #     self.sidebar.item(idx, 0).setBackground(QtGui.QColor(22, 41, 85))
        self.sidebar.resizeColumnsToContents()
        self.sidebar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  
    
    def populate_status_bar(self, row, start, end):
        self.status_bar.setText(''.join(self.df.iloc[row:row+1, start:end+1].to_string(header=False, index=False)))

    
    def populate_flows(self, flows):
        self.flows.setColumnCount(1)
        self.flows.setRowCount(len(flows))
        for idx, row in enumerate(flows):
            self.flows.setItem(idx,0, QTableWidgetItem(row))
        self.flows.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.flows.resizeColumnsToContents()

    def populate_actions(self, actions):
        self.actions.setColumnCount(1)
        self.actions.setRowCount(len(actions))
        for idx, row in enumerate(actions):
            self.actions.setItem(idx,0, QTableWidgetItem(row))
        self.actions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.actions.resizeColumnsToContents()

    def btn_left(self):
        if self.cell_selector.currentIndex() > 0:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() - 1)

    def btn_right(self):
        if self.cell_selector.currentIndex() < self.header_len - self.cell_selector_start - 1:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() + 1)

    def btn_up(self):
        pass
    def btn_down(self):
        pass
    def btn_save(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
