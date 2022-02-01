import sys
import re
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
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
        self.canned_states = {}
        self.action_states = {}
        self.flow_states = {}

        # Sets the starting column number for the cell selector combo box
        self.cell_selector_start = 4

        loadUi('main_window.ui', self)
        self.setWindowTitle('CE Studio')
        
        # Connecting functions
        [self.sidebar.selectionModel().selectionChanged.connect(x) for x in 
        [self.row_selector, self.clear_selections]]
        self.cell_selector.currentIndexChanged.connect(self.populate_analysis)
        self.analysis.textChanged.connect(self.save_analysis)
        self.left.clicked.connect(self.btn_left)
        self.right.clicked.connect(self.btn_right)
        self.down.clicked.connect(self.btn_down)
        self.up.clicked.connect(self.btn_up)
        self.save.clicked.connect(self.btn_save)
        self.flows.itemSelectionChanged.connect(self.flows_selection)
        # self.analysis.cursorPositionChanged.connect(self.test)

        # Methods to be executed on startup
        self.populate_canned()
        self.populate_flows(example_flows)
        self.populate_actions(example_actions)

        # Executed on excel.load
        self.df = excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        excel.incomplete(self.df)
        self.populate_sidebar()
        index = self.sidebar.model().index(0, 0)
        self.sidebar.selectionModel().select(
            index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)
        self.populate_status_bar(2, 0, 2)
        self.populate_cell_selector(self.cell_selector_start, -1)
        
        
        self.populate_chat()

        # Tests
        # print(xw.books.active.name)
        # print(self.df.head)


    def row_selector(self, selected):
        '''
        Master Controller. Keeps the current row number updated
        '''
        idx = selected.indexes()
        if len(idx) > 0:
            self.row = idx[0].row()
        self.sidebar.scrollToItem(self.sidebar.item(self.row, 0))
        self.populate_analysis()
    
    def clear_selections(self):
        self.flows.clearSelection()
        self.actions.clearSelection()
        # self.canned.rb_group.setChecked(False)

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
            # combo.setStyleSheet('selection-background-color: red;')
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
        '''
        Highlights and unhighlights the user selected text
        '''
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4294901760:
            format.setBackground(Qt.red)
            # format.setBackground(QColor(55, 92, 123))
        else:
            format.clearBackground()
        cursor.setCharFormat(format)

    def highlight(self):
        '''
        Highlights predefined patterns in the chat log
        '''
        class_format = QTextCharFormat()
        class_format.setBackground(Qt.red)
        class_format.setFontWeight(QFont.Bold)
        # pattern = INSERT REGEX PATTERN HERE
        self.highlighter.add_mapping(class_format)
        # class_format.setTextColor(QColor(120, 135, 171))


    def populate_analysis(self):
        self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex()+self.cell_selector_start])

    def populate_cell_selector(self, start, end):
        for item in list(self.df.columns.values)[start:end]:
            self.cell_selector.addItem(item)


    def populate_canned(self):
        self.canned.setColumnCount(4)
        self.canned.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned.setItem(idx,0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName='rb_group')
            rb_group.idReleased.connect(self.canned_selection)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                rb_group.addButton(combo)
                self.canned.setCellWidget(idx, i+1, combo)
        # self.canned.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.canned.resizeColumnsToContents()
        # self.canned.setColumnWidth(0, 320)

    def canned_selection(self):
        '''
        Keeps track of selected radiobuttons for each row of the excel file
        '''
        btn = self.sender()
        if self.row not in self.canned_states:
            self.canned_states[self.row] = {btn.objectName():btn.checkedButton().text()}
        else:
            self.canned_states[self.row][btn.objectName()] = btn.checkedButton().text()


    def populate_sidebar(self):
        self.sidebar.setColumnCount(1)
        self.sidebar.setRowCount(len(self.df.index))
        for idx, row in self.df.iterrows():
            self.sidebar.setItem(idx,0, QTableWidgetItem(str(idx + 1)))
            if row['bool_check'] == 1:
                self.sidebar.item(idx, 0).setBackground(QtGui.QColor(120, 120, 120))
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


    def flows_selection(self):
        cells = self.sender()

        # self.flows.setSelected()

        # self.flow_states[self.row] = cells.selectedItems()
        # print(self.flow_states)


        # print(cells.selectedItems())
        # if self.row not in self.flow_states:
        #     self.canned_states[self.row] = {btn.objectName():btn.checkedButton().text()}
        #     print('not')
        # else:
        #     self.canned_states[self.row][btn.objectName()] = btn.checkedButton().text()
        #     print ('in')

    def populate_actions(self, actions):
        self.actions.setColumnCount(1)
        self.actions.setRowCount(len(actions))
        for idx, row in enumerate(actions):
            self.actions.setItem(idx,0, QTableWidgetItem(row))
        self.actions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.actions.resizeColumnsToContents()

    ############################################################
    # Buttons
    ############################################################
    def btn_left(self):
        if self.cell_selector.currentIndex() > 0:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() - 1)

    def btn_right(self):
        if self.cell_selector.currentIndex() < self.header_len - self.cell_selector_start - 1:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() + 1)

    def btn_up(self):
        if self.row > 0:
            index = self.sidebar.model().index(self.row - 1, 0)
            self.sidebar.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_down(self):
        if self.row < self.index_len:
            index = self.sidebar.model().index(self.row + 1, 0)
            self.sidebar.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_save(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
