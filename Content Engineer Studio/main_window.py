import sys
import re
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
# from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat
from excel_helpers import * 
from data import *
from stylesheets import *

class Highlighter(QSyntaxHighlighter):
    '''
    For highlighting anonymized text blocks
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    def add__mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.setFormat(start, end-start, fmt)


class TextEdit(QTextEdit):
    '''
    For auto resizing text edits in tables
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
    

########################################################################################
# Main
########################################################################################
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.row = 0
        self.header_len = 0
        self.index_len = 0
        self.highlighter = Highlighter()

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
        # self.analysis.cursorPositionChanged.connect(self.test)

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
        # print(xw.books.active.name)
        # print(self.df.head)


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
            oname1, oname2 = 'chat_bubble_bot', 'chat_bubble_customer'
            if idx % 2 == 0:
                combo = TextEdit(self, objectName=oname1) 
            else:
                combo = TextEdit(self, objectName=oname2) 
            self.chat.setCellWidget(idx, 0, combo)
            combo.setText(message)
            if idx % 2 == 0:
                combo.setAlignment(Qt.AlignRight)
            combo.setStyleSheet('selection-background-color: red;')
            combo.textChanged.connect(lambda idx=idx: self.chat.resizeRowToContents(idx))
            combo.cursorPositionChanged.connect(self.highlight_selection)
        self.chat.installEventFilter(self)
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def eventFilter(self, source, event):
        '''
        Intercepts resize events for the table widget
        '''
        if event.type() == event.Resize:
            QTimer.singleShot(0, self.chat.resizeRowsToContents)
        return super().eventFilter(source, event)

    def highlight_selection(self):
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4294901760:
            format.setBackground(Qt.red)
        else:
            format.setBackground(QColor(70, 70, 70))
        cursor.setCharFormat(format)

    def highlight(self):
        '''
        Highlights the user selected text
        '''
        class_format = QTextCharFormat()
        class_format.setBackground(Qt.red)
        class_format.setFontWeight(QFont.Bold)
        # pattern = INSERT REGEX PATTERN HERE
        self.highlighter.add_mapping(class_format)
        # class_format.setTextColor(QColor(120, 135, 171))


    def populate_analysis(self, signal):
        self.analysis.setText(self.df.loc[self.row][signal+self.cell_selector_start])

    def populate_cell_selector(self, start, end):
        for item in list(self.df.columns.values)[start:end]:
            self.cell_selector.addItem(item)

    def populate_canned(self):
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
                self.sidebar.item(idx, 0).setBackground(QtGui.QColor(120, 120, 120))
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
