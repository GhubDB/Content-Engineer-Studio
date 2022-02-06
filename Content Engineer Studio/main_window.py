import sys
import re
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat
from excel_helpers import * 
from selenium_helpers import *
from data import *
from stylesheets import *
from bs4 import BeautifulSoup

'''class Finder(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        searchbar.textChanged.connect(self.filter_proxy_model.setFilterRegExp)'''

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

        self.excel = Excel()
        self.highlighter = Highlighter()
        self.scraper = MainDriver()
        self.row = 0
        self.row_2 = 0
        self.header_len_2 = 0
        self.header_len = 0
        self.index_len = 0
        self.index_len_2 = 0
        # Keeps track of the sum of df.bool_check in order to find out if row colors need to be changed.
        self.repopulate_sidebar = 0
        self.repopulate_sidebar_2 = 0
        self.canned_states = {}
        self.action_states = {} #not implemented
        self.flow_states = {} #not implemented
        self.marked_messages = []
        self.marked_messages_2 = []
        self.filter_proxy_model = ''

        self.wb = ''
        self.wb_2 = ''
        self.wb_faq = ''

        # Sets the starting column number for the cell selector combo boxt
        self.cell_selector_start = 6
        self.cell_selector_start_2 = 2

        loadUi('main_window.ui', self)
        self.setWindowTitle('Content Engineer Studio')
        
        # Connecting functions
        [self.sidebar.selectionModel().selectionChanged.connect(x) for x in 
        [self.row_selector, self.clear_selections]]
        self.sidebar_2.selectionModel().selectionChanged.connect(self.row_selector_2)
        self.cell_selector.currentIndexChanged.connect(self.populate_analysis)
        self.cell_selector_2.currentIndexChanged.connect(self.populate_analysis_2)
        self.analysis.textChanged.connect(self.save_analysis)
        self.analysis_2.textChanged.connect(self.save_analysis_2)
        self.left.clicked.connect(self.btn_left)
        self.left_2.clicked.connect(self.btn_left_2)
        self.right.clicked.connect(self.btn_right)
        self.right_2.clicked.connect(self.btn_right_2)
        self.down.clicked.connect(self.btn_down)
        self.down_2.clicked.connect(self.btn_down_2)
        self.up.clicked.connect(self.btn_up)
        self.up_2.clicked.connect(self.btn_up_2)
        self.save.clicked.connect(self.btn_save)
        self.save_2.clicked.connect(self.btn_save_2)
        self.flows.itemSelectionChanged.connect(self.flows_selection) # not implemented
        self.switch_to_analysis_suite.clicked.connect(self.switchToAnalysis)
        self.export_to_testing_suite.clicked.connect(self.switchToTesting)
        self.switch_to_testing_suite.clicked.connect(self.switchToTesting)

        # Executed on excel.load
        self.df, self.wb = self.excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.excel.incomplete(self.df, self.cell_selector_start, len(self.df.columns))
        self.populate_sidebar()
        self.faq, self.wb_faq = self.excel.load('recipes.xlsx', 'Sheet1')
        
        # Executed on excel.load
        self.df_2, self.wb_2 = self.excel.load('testing.xlsx', 'Sheet1')
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.excel.incomplete(self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
        self.populate_sidebar_2()

        # Adding search box
        self.populate_search_column_select()
        model = QStandardItemModel(len(self.faq.index), 1)
        for idx, _ in enumerate(self.faq.iterrows()):
            item = QStandardItem(self.faq[self.search_column_select.currentText()][idx])
            model.setItem(idx, 0 , item)
        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)
        self.search_box.setModel(filter_proxy_model)
        self.searchbar.textChanged.connect(filter_proxy_model.setFilterRegExp)
        self.search_column_select.currentIndexChanged.connect(self.populate_search_box)

        # Adding search box_2
        self.populate_search_column_select_2()
        model = QStandardItemModel(len(self.faq.index), 1)
        for idx, _ in enumerate(self.faq.iterrows()):
            item = QStandardItem(self.faq[self.search_column_select_2.currentText()][idx])
            model.setItem(idx, 0 , item)
        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)
        self.search_box_2.setModel(filter_proxy_model)
        self.searchbar_2.textChanged.connect(filter_proxy_model.setFilterRegExp)
        self.search_column_select_2.currentIndexChanged.connect(self.populate_search_box)

        # Methods to be executed on startup
        self.populate_canned()
        self.populate_flows(example_flows)
        self.populate_actions(example_actions)
        # self.populate_search_column_select()

        '''Sets sidebar to first item selected on startup'''
        # index = self.sidebar.model().index(0, 0)
        # self.sidebar.selectionModel().select(
        #     index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

        self.populate_status_bar(2, 0, 2)
        self.populate_cell_selector(self.cell_selector_start, self.header_len+1)
        self.populate_cell_selector_2(self.cell_selector_start_2, self.header_len_2+1)
        
        

        # Tests
        # print(xw.books.active.name)
        # print(self.df.head)

    ################################################################################################
    '''
    Main Methods
    '''
    ################################################################################################


    def row_selector(self, selected):
        '''
        Master Controller. Keeps the current row number updated
        '''
        # Save and clean up before next row is loaded
        self.saveOnRowChange()
        self.clearChat()
        self.marked_messages = []

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row:
            self.row = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df, self.wb = self.excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.excel.incomplete(self.df, self.cell_selector_start, len(self.df.columns))
        self.populate_sidebar()

        # Loading web page, web scraping and adding results to self.chat

        self.scraper.setUp(url=self.df.iloc[self.row, 3])
        chat_text = self.scraper.cleverbot()
        self.populate_chat(chat_text)

        # Autoscrolling to the selection on the sidebar
        self.sidebar.scrollToItem(self.sidebar.item(self.row, 0))

        self.populate_canned()
        self.populate_analysis()

    def saveOnRowChange(self):
        '''
        Saves current states to Excel
        '''
        # Saving chat messages
        if len(self.marked_messages) > 0:
            customer, bot  = self.getChatText()
            self.excel.updateCells(customer, self.row + 2, 5)
            self.excel.updateCells(bot, self.row + 2, 6)
        
        # Saving analysis contents
        self.excel.updateCells(self.df.iloc[self.row:self.row+1, self.cell_selector_start:self.header_len].values, 
            self.row + 2, self.cell_selector_start + 1)

        # Saves the excel file
        self.excel.saveWB(self.wb)

    def eventFilter(self, source, event):
        '''
        Filters Events and calls the respective functions
        '''
        if event.type() == event.Resize:
            QTimer.singleShot(0, self.chat.resizeRowsToContents)
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                # print(source.objectName())
                QTimer.singleShot(0, lambda x=event, y=source: self.select_chat(x, y))
        return super().eventFilter(source, event)
    
    def clear_selections(self):
        self.flows.clearSelection()
        self.actions.clearSelection()
        # self.canned.rb_group.setChecked(False)

    def save_analysis(self):
        '''
        Saves current analysis text to dataframe
        '''
        self.df.loc[self.row][self.cell_selector.currentText()] = self.analysis.toPlainText()
    
    def populate_chat(self, chat):
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(chat))
        for idx, sender,  in enumerate(chat):
            if sender[0] == 'bot':
                combo = TextEdit(self, objectName=f'bot_{idx}') 
            else:
                combo = TextEdit(self, objectName=f'customer_{idx}') 
            self.chat.setCellWidget(idx, 0, combo)
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            # Bot
            if sender[0] == 'bot':
                combo.setStyleSheet('font-size: 11pt;\
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 5px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    padding-right: 4px;')
                combo.setAlignment(Qt.AlignRight)
            # customer
            else:
                combo.setStyleSheet('font-size: 11pt; \
                                    border-style: outset; \
                                    border-left-width: 5px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(90, 90, 90);')
            combo.textChanged.connect(lambda idx=idx: self.chat.resizeRowToContents(idx))
            combo.cursorPositionChanged.connect(self.highlight_selection)
        self.chat.installEventFilter(self)
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def clearChat(self):
        # self.chat.clear()
        self.chat.setRowCount(0)


    def select_chat(self, event, source):
        '''
        Handles highlighting of user selected chat messages and adding them to a data structure
        '''
        if 'bot' in source.objectName():
            if source.objectName() not in self.marked_messages:
                self.marked_messages.append(source.objectName())
                source.setStyleSheet('font-size: 11pt;\
                                    font-weight: bold; \
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 10px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    border-left-width: 2px;\
                                    border-left-color: rgb(45, 136, 45);\
                                    border-top-width: 2px;\
                                    border-top-color: rgb(45, 136, 45);\
                                    border-bottom-width: 2px;\
                                    border-bottom-color: rgb(45, 136, 45);\
                                    background-color: rgb(70, 81, 70); \
                                    padding-right: 4px;')
                source.setAlignment(Qt.AlignRight)  
            else:
                self.marked_messages.remove(source.objectName())
                source.setStyleSheet('font-size: 11pt;\
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 5px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    background-color: rgb(70, 70, 70); \
                                    padding-right: 4px;')
                source.setAlignment(Qt.AlignRight)

        else:
            if source.objectName() not in self.marked_messages:
                self.marked_messages.append(source.objectName())
                source.setStyleSheet('font-size: 11pt; \
                                    font-weight: bold; \
                                    border-style: outset; \
                                    border-left-width: 10px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    border-right-width: 2px; \
                                    border-right-color: rgb(83, 43, 114); \
                                    border-top-width: 2px; \
                                    border-top-color: rgb(83, 43, 114); \
                                    border-bottom-width: 2px; \
                                    border-bottom-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(74, 69, 78);')
            else:
                self.marked_messages.remove(source.objectName())
                source.setStyleSheet('font-size: 11pt; \
                                    border-style: outset; \
                                    border-left-width: 5px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(90, 90, 90);')
    

    def getChatText(self):
        '''
        Pulls and anonymizes user selected messages from the chat tablewidget. Returns dict of messages.
        '''
        bot = []
        customer = []
        message_cells = []
        # Isolate numbers from list of selected message object names and add the sorted output to new list
        if len(self.marked_messages) > 0:
            [message_cells.append(message.split('_')) for message in self.marked_messages]
            message_cells = sorted(message_cells, key = lambda x: x[1])
            # Iterate over selected chat messages
            for message, idx in message_cells:
                # Convert the text of the message at the grid location to HTML and parse it
                message_html = BeautifulSoup(self.chat.cellWidget(int(idx), 0).toHtml(), 'html.parser')
                # Find all span tags and replace the text with ***
                tags = message_html.find_all('span')
                for tag in tags:
                    tag.string = '***'
                if 'bot' in message:
                    bot.append(message_html.get_text())
                else:
                    customer.append(message_html.get_text())
            return ''.join(customer), ''.join(bot)


    def highlight_selection(self):
        '''
        Highlights and unhighlights user selected text
        '''
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4282679021:
            format.setBackground(QColor(68, 126, 237))
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


    def populate_cell_selector(self, start, end):
        for item in list(self.df.columns.values)[start:end]:
            self.cell_selector.addItem(item)


    def populate_analysis(self):
        # '''Bugfix for number only entries on the excel sheet needed. 
        #   File "c:\Users\Me\Dropbox\Python\Content Engineer Studio\main_window.py", line 348, in populate_analysis
        # self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])
        # TypeError: setText(self, str): argument 1 has unexpected type numpy.float64'''
        print(self.row, 'no1', self.cell_selector.currentIndex() + self.cell_selector_start)
        self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])

    
    def populate_search_column_select(self):
        for item in list(self.faq.columns.values):
            self.search_column_select.addItem(item)
  

    def populate_search_box(self):
        '''
        Populates the search box with values from FAQ excel sheet
        '''
        model = QStandardItemModel(len(self.faq.index), 1)        
        for idx, _ in enumerate(self.faq.iterrows()):
            item = QStandardItem(self.faq[self.search_column_select.currentText()][idx])
            model.setItem(idx, 0 , item)

        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)
        self.search_box.setModel(filter_proxy_model)
        self.searchbar.textChanged.connect(filter_proxy_model.setFilterRegExp)

        

    def populate_canned(self):
        # Radiobuttons
        self.canned.setColumnCount(len(canned_questions )+1)
        self.canned.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned.setItem(idx,0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName=f'rb_group_{idx}')
            oname = f'rb_group_{idx}'
            rb_group.idReleased.connect(self.canned_selection)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                # combo.setId(i)
                if self.row in self.canned_states:
                    if oname in self.canned_states[self.row]:
                        if self.canned_states[self.row][oname] == choice:
                            combo.setChecked(True)
                rb_group.addButton(combo)
                self.canned.setCellWidget(idx, i+1, combo)
        self.canned.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.canned.resizeColumnsToContents()
        self.canned.horizontalHeader().resizeSection(1, 50)
        self.canned.horizontalHeader().resizeSection(2, 55)
        self.canned.horizontalHeader().resizeSection(3, 85)
        # self.canned.horizontalHeader().resizeSection(4, 70)

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


    def getCanned(self):
        pass

    def populate_sidebar(self):
        self.sidebar.setColumnCount(1)
        self.sidebar.setRowCount(self.index_len)
        [self.sidebar.setItem(idx,0, QTableWidgetItem(str(idx + 2))) for idx in range(0, self.index_len)]
        [self.sidebar.item(idx, 0).setBackground(QtGui.QColor(120, 120, 120)) 
            for idx, row in self.completed.iterrows() if row.all()]
        self.sidebar.resizeColumnsToContents()
        self.sidebar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

  
    def populate_status_bar(self, row, start, end):
        self.status_bar.setText(self.df.iloc[row:row+1, start:end+1].to_string(header=False, index=False))

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

    ################################################################################################
    '''
    Buttons
    '''
    ################################################################################################
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
        self.saveOnRowChange()
        # print(self.chat.cellWidget(0, 0).document())

    def switchToAnalysis(self):
        self.stackedWidget.setCurrentWidget(self.analysis_suite)

    def switchToTesting(self):
        self.stackedWidget.setCurrentWidget(self.testing_suite)

    def ExportToTesting(self):
        self.stackedWidget.setCurrentWidget(self.testing_suite)

    ################################################################################################
    '''
    Test Suite
    '''
    ################################################################################################

    def row_selector_2(self, selected):
        '''
        Master Controller. Keeps the current row number updated
        '''
        # Save and clean up before next row is loaded
        self.saveOnRowChange_2()
        self.clearChat_2()
        self.marked_messages_2 = []

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row_2:
            self.row_2 = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df_2, self.wb_2 = self.excel.load('testing.xlsx', 'Sheet1')
        self.header_len_2 = len(self.df.columns)
        self.index_len_2 = len(self.df.index)
        self.completed_2 = self.excel.incomplete(self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
        self.populate_sidebar_2()

        # Loading web page, web scraping and adding results to self.chat_2
        # self.scraper.setUp(url='https://www.cleverbot.com/')
        # chat_text = self.scraper.cleverbot_2()
        # self.populate_chat_2(chat_text)

        # Autoscrolling to the selection on the sidebar
        self.sidebar_2.scrollToItem(self.sidebar.item(self.row, 0))

        self.populate_canned_2()
        self.populate_analysis_2()

    def saveOnRowChange_2(self):
        '''
        Saves current states to Excel
        '''
        # Saving chat messages
        if len(self.marked_messages_2) > 0:
            customer, bot  = self.getChatText_2()
            self.excel.updateCells(customer, self.row_2 + 2, 4)
            self.excel.updateCells(bot, self.row_2 + 2, 5)
        
        # Saving analysis contents
        self.excel.updateCells(self.df_2.iloc[self.row_2:self.row_2+1, self.cell_selector_start_2:self.header_len_2].values, 
            self.row_2 + 2, self.cell_selector_start_2 + 1)

        # Saves the excel file
        self.excel.saveWB(self.wb_2) 

    def save_analysis_2(self):
        '''
        Saves current analysis text to dataframe
        '''
        # print(self.row_2, self.cell_selector_2.currentText(), self.cell_selector_2.currentText())
        # self.df_2.loc[self.row_2][self.cell_selector_2.currentText()] = self.cell_selector_2.currentText()
    
    def populate_chat_2(self, chat):
        self.chat_2.setColumnCount(1)
        self.chat_2.setRowCount(len(chat))
        for idx, sender,  in enumerate(chat):
            if sender[0] == 'bot':
                combo = TextEdit(self, objectName=f'bot_{idx}') 
            else:
                combo = TextEdit(self, objectName=f'customer_{idx}') 
            self.chat_2.setCellWidget(idx, 0, combo)
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            # Bot
            if sender[0] == 'bot':
                combo.setStyleSheet('font-size: 11pt;\
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 5px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    padding-right: 4px;')
                combo.setAlignment(Qt.AlignRight)
            # customer
            else:
                combo.setStyleSheet('font-size: 11pt; \
                                    border-style: outset; \
                                    border-left-width: 5px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(90, 90, 90);')
            combo.textChanged.connect(lambda idx=idx: self.chat_2.resizeRowToContents(idx))
            combo.cursorPositionChanged.connect(self.highlight_selection_2)
        self.chat_2.installEventFilter(self)
        self.chat_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def clearChat_2(self):
        # self.chat.clear()
        self.chat_2.setRowCount(0)


    def select_chat_2(self, event, source):
        '''
        Handles highlighting of user selected chat messages and adding them to a data structure
        '''
        if 'bot' in source.objectName():
            if source.objectName() not in self.marked_messages_2:
                self.marked_messages_2.append(source.objectName())
                source.setStyleSheet('font-size: 11pt;\
                                    font-weight: bold; \
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 10px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    border-left-width: 2px;\
                                    border-left-color: rgb(45, 136, 45);\
                                    border-top-width: 2px;\
                                    border-top-color: rgb(45, 136, 45);\
                                    border-bottom-width: 2px;\
                                    border-bottom-color: rgb(45, 136, 45);\
                                    background-color: rgb(70, 81, 70); \
                                    padding-right: 4px;')
                source.setAlignment(Qt.AlignRight)  
            else:
                self.marked_messages_2.remove(source.objectName())
                source.setStyleSheet('font-size: 11pt;\
                                    text-align: right; \
                                    border-style: outset;\
                                    border-right-width: 5px;\
                                    border-right-color: rgb(45, 136, 45);\
                                    background-color: rgb(70, 70, 70); \
                                    padding-right: 4px;')
                source.setAlignment(Qt.AlignRight)

        else:
            if source.objectName() not in self.marked_messages_2:
                self.marked_messages_2.append(source.objectName())
                source.setStyleSheet('font-size: 11pt; \
                                    font-weight: bold; \
                                    border-style: outset; \
                                    border-left-width: 10px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    border-right-width: 2px; \
                                    border-right-color: rgb(83, 43, 114); \
                                    border-top-width: 2px; \
                                    border-top-color: rgb(83, 43, 114); \
                                    border-bottom-width: 2px; \
                                    border-bottom-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(74, 69, 78);')
            else:
                self.marked_messages_2.remove(source.objectName())
                source.setStyleSheet('font-size: 11pt; \
                                    border-style: outset; \
                                    border-left-width: 5px; \
                                    border-left-color: rgb(83, 43, 114); \
                                    padding-left: 4px; \
                                    background-color: rgb(90, 90, 90);')
    

    def getChatText_2(self):
        '''
        Pulls and anonymizes user selected messages from the chat tablewidget. Returns dict of messages.
        '''
        bot = []
        customer = []
        message_cells = []
        # Isolate numbers from list of selected message object names and add the sorted output to new list
        if len(self.marked_messages_2) > 0:
            [message_cells.append(message.split('_')) for message in self.marked_messages]
            message_cells = sorted(message_cells, key = lambda x: x[1])
            # Iterate over selected chat messages
            for message, idx in message_cells:
                # Convert the text of the message at the grid location to HTML and parse it
                message_html = BeautifulSoup(self.chat_2.cellWidget(int(idx), 0).toHtml(), 'html.parser')
                # Find all span tags and replace the text with ***
                tags = message_html.find_all('span')
                for tag in tags:
                    tag.string = '***'
                if 'bot' in message:
                    bot.append(message_html.get_text())
                else:
                    customer.append(message_html.get_text())
            return ''.join(customer), ''.join(bot)


    def highlight_selection_2(self):
        '''
        Highlights and unhighlights user selected text
        '''
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4282679021:
            format.setBackground(QColor(68, 126, 237))
        else:
            format.clearBackground()
        cursor.setCharFormat(format)

    def highlight_2(self):
        '''
        Highlights predefined patterns in the chat log
        '''
        class_format = QTextCharFormat()
        class_format.setBackground(Qt.red)
        class_format.setFontWeight(QFont.Bold)
        # pattern = INSERT REGEX PATTERN HERE
        self.highlighter.add_mapping(class_format)
        # class_format.setTextColor(QColor(120, 135, 171))


    def populate_cell_selector_2(self, start, end):
        for item in list(self.df_2.columns.values)[start:end]:
            self.cell_selector_2.addItem(item)


    def populate_analysis_2(self):
        # '''Bugfix for number only entries on the excel sheet needed. 
        #   File "c:\Users\Me\Dropbox\Python\Content Engineer Studio\main_window.py", line 348, in populate_analysis
        # self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])
        # TypeError: setText(self, str): argument 1 has unexpected type numpy.float64'''
        # print(self.row_2, self.cell_selector_2.currentIndex() + self.cell_selector_start_2)
        # print(self.df.head)
        # self.analysis_2.setText(self.df_2.loc[1][3])
        self.analysis_2.setText(self.df_2.loc[self.row_2][self.cell_selector_2.currentIndex() + self.cell_selector_start_2])

    
    def populate_search_column_select_2(self):
        for item in list(self.faq.columns.values):
            self.search_column_select_2.addItem(item)
  

    def populate_search_box_2(self):
        '''
        Populates the search box with values from FAQ excel sheet
        '''
        model = QStandardItemModel(len(self.faq.index), 1)        
        for idx, _ in enumerate(self.faq.iterrows()):
            item = QStandardItem(self.faq[self.search_column_select_2.currentText()][idx])
            model.setItem(idx, 0 , item)

        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)
        self.search_box_2.setModel(filter_proxy_model)
        self.searchbar_2.textChanged.connect(filter_proxy_model.setFilterRegExp)

        

    def populate_canned_2(self):
        # Radiobuttons
        self.canned_2.setColumnCount(len(canned_questions )+1)
        self.canned_2.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned_2.setItem(idx,0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName=f'rb_group_2_{idx}')
            oname = f'rb_group_2_{idx}'
            rb_group.idReleased.connect(self.canned_selection_2)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                # combo.setId(i)
                if self.row in self.canned_states_2:
                    if oname in self.canned_states_2[self.row]:
                        if self.canned_states_2[self.row][oname] == choice:
                            combo.setChecked(True)
                rb_group.addButton(combo)
                self.canned_2.setCellWidget(idx, i+1, combo)
        self.canned_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.canned.resizeColumnsToContents()
        self.canned_2.horizontalHeader().resizeSection(1, 50)
        self.canned_2.horizontalHeader().resizeSection(2, 55)
        self.canned_2.horizontalHeader().resizeSection(3, 85)
        # self.canned.horizontalHeader().resizeSection(4, 70)

        # self.canned.setColumnWidth(0, 320)

    def canned_selection_2(self):
        '''
        Keeps track of selected radiobuttons for each row of the excel file
        '''
        btn = self.sender()
        if self.row not in self.canned_states_2:
            self.canned_states_2[self.row_2] = {btn.objectName():btn.checkedButton().text()}
        else:
            self.canned_states_2[self.row_2][btn.objectName()] = btn.checkedButton().text()


    def getCanned_2(self):
        pass

    def populate_sidebar_2(self):
        self.sidebar_2.setColumnCount(1)
        self.sidebar_2.setRowCount(self.index_len)
        [self.sidebar_2.setItem(idx,0, QTableWidgetItem(str(idx + 2))) for idx in range(0, self.index_len_2)]
        [self.sidebar_2.item(idx, 0).setBackground(QtGui.QColor(120, 120, 120)) 
            for idx, row in self.completed_2.iterrows() if row.all()]
        self.sidebar_2.resizeColumnsToContents()
        self.sidebar_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

  
    # def populate_status_bar_2(self, row, start, end):
    #     self.status_bar_2.setText(self.df_2.iloc[row:row+1, start:end+1].to_string(header=False, index=False))


    ################################################################################################
    # Buttons
    ################################################################################################
    def btn_left_2(self):
        if self.cell_selector_2.currentIndex() > 0:
            self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() - 1)

    def btn_right_2(self):
        if self.cell_selector_2.currentIndex() < self.header_len_2 - self.cell_selector_start_2 - 1:
            self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() + 1)

    def btn_up_2(self):
        if self.row_2 > 0:
            index = self.sidebar_2.model().index(self.row - 1, 0)
            self.sidebar_2.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_down_2(self):
        if self.row_2 < self.index_len:
            index = self.sidebar_2.model().index(self.row + 1, 0)
            self.sidebar_2.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_save_2(self):
        self.saveOnRowChange_2()

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
