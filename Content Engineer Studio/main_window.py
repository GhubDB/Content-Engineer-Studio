import sys, re, time, traceback
from threading import Thread
from warnings import filters
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import QStandardItemModel, QStandardItem, \
    QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QTextCursor
from excel_helpers import * 
from selenium_helpers import *
from data import *
from stylesheets import *
from bs4 import BeautifulSoup

class Worker(QRunnable):
    '''
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
    kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add callback to kwargs where necessary.
        if 'activate_output' in args:
            self.kwargs['output'] = self.signals.output
            self.args = self.args[:-2]

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info() [:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished - No data
    error - tuple (exctype, value, traceback.format_exc() )
    result - object data returned from processing, anything
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    output = pyqtSignal(object)
    progress = pyqtSignal(int)

class AutoQueueModel(QStandardItemModel):
    pass
    # def itemData(self, itemData):
    #     dicti = super().itemData(itemData)
    #     print(dicti)
    #     [item.remove('BackgroundRole') for item in dicti if 'BackgroundRole' in item]
    #     return

class FaqAutoSearch(QWidget):
    '''
    Implements a window that allows the user to search for FAQ's
    '''
    def __init__(self, parent=None, value=None):
        super(FaqAutoSearch, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("FAQ's")
        self.setStyleSheet('background-color: rgb(70, 70, 70);')
        table = QTableView(objectName='faq_table')
        table.setModel(win.faq_auto_search_model)
        table.setMinimumHeight(500)
        table.setMinimumWidth(1400)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.setStyleSheet('background-color: rgb(50, 50, 50);')
        faq_search = QLineEdit()
        faq_search.textChanged.connect(win.faq_auto_search_model.setFilterRegExp)
        faq_search.setText(value)
        faq_search.setStyleSheet('background-color: rgb(50, 50, 50);')
        
        # Search key column selector
        self.faq_selector = QComboBox()
        for item in list(win.faq_df.columns.values):
            self.faq_selector.addItem(item)
            
        self.layout = QVBoxLayout()
        self.layout.addWidget(table)
        self.layout.addWidget(self.faq_selector)
        self.layout.addWidget(faq_search)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalScrollBar().hide()
        table.horizontalScrollBar().hide()
        self.setLayout(self.layout)
        self.setStyleSheet(elegantdark)
        self.show()
        self.faq_selector.currentIndexChanged.connect(self.setSearchColumn)

    def setSearchColumn(self):
        '''
        This enables selecting the column to search in
        '''
        idx = self.faq_selector.currentIndex()
        win.faq_auto_search_model.setFilterKeyColumn(idx)


class CESdialog(QDialog):
    '''
    Custom user interface dialog
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alert!")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Please open a new dialog before sending messages.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Highlighter(QSyntaxHighlighter):
    '''
    Highlights predefined regular expressions in the chat log
    '''
    def __init__(self, document, name, parent=None):
        super().__init__(parent)
        self._mapping = {}
        self.name = name
        
        # Email addresses
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        # class_format.setFontWeight(QFont.Bold)  
        pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" # Working changes
        # pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" # Original
        self.add_mapping(pattern, class_format)
        
        # Phone numbers
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        # class_format.setFontWeight(QFont.Bold)        
        pattern = r"(\b(0041|0)|\B\+41)(\s?\(0\))?([\s\-./,'])?[1-9]{2}([\s\-./,'])?[0-9]{3}([\s\-./,'])?[0-9]{2}([\s\-./,'])?[0-9]{2}\b"
        # class_format.setTextColor(QColor(120, 135, 171))
        self.add_mapping(pattern, class_format)
        
        self.setDocument(document)

    def add_mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        '''
        Reimplemented highlighting function
        '''
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                win.auto_anonymized.append([self.name, start, end])
                
                # self.setFormat(start, end-start, fmt) # Original implementation

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
    '''
    Main application
    '''
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # URLs
        self.livechat_url = 'https://www.cleverbot.com/'

        # Sets the starting column number for the cell selector combo box
        self.cell_selector_start = 6
        self.cell_selector_start_2 = 4

        # Sets the number of prebuffered windows for auto mode
        self.buffer_len = 2

        # Instantiating classes
        self.threadpool = QThreadPool()
        self.is_webscraping = False
        self.analysis_excel = Excel()
        self.testing_excel = Excel()
        self.faq_excel = Excel()
        self.browsers = [Browser() for i in range(0, self.buffer_len)]

        # Breaks the buffering loop
        self.buffering = False
        
        self.current_browser = 0
        self.questions = []
        self.highlighters = {}
        self.row = 0
        self.row_2 = 0
        self.header_len = 0
        self.header_len_2 = 0
        self.index_len = 0
        self.index_len_2 = 0
        self.dialog_num = 0
        self.canned_states = {}
        self.canned_states_2 = {}
        self.marked_messages = []
        self.marked_messages_2 = []
        self.chat_test = []
        self.filter_proxy_model = ''
        self.auto_anonymized = []

        # Load Ui file, set settings
        loadUi('main_window.ui', self)
        self.setWindowTitle('Content Engineer Studio')
        self.setContentsMargins(0, 0, 0, 0)

        # Create model for auto_queue and history
        self.history_model = QStandardItemModel()
        self.history.setModel(self.history_model)
        self.history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Test items
        items = ['Hello there.', 'How are you today?', 'What are you doing today?']
        for item in items:
            items = QtGui.QStandardItem(item)
            self.history_model.appendRow(items) 

        # Setting up Auto Queue
        self.auto_queue_model = AutoQueueModel()
        self.auto_queue.setModel(self.auto_queue_model)
        self.auto_queue.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.auto_queue.installEventFilter(self)

        # Installing Event filters
        self.analysis.installEventFilter(self)
        self.analysis_2.installEventFilter(self)
        
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
        self.switch_to_analysis_suite.clicked.connect(self.switchToAnalysis)
        self.export_to_testing_suite.clicked.connect(self.exportToTesting)
        self.switch_to_testing_suite.clicked.connect(self.switchToTesting)
        self.colorize.clicked.connect(self.btn_colorize)
        self.colorize_2.clicked.connect(self.btn_colorize_2)
        self.chat_input.returnPressed.connect(self.send_btn)
        self.send.clicked.connect(self.send_btn)
        self.new_dialog.clicked.connect(self.new_dialog_btn)
        self.next_question.clicked.connect(self.next_btn)
        self.searchbar_2.textChanged.connect(lambda: self.search_box_2.setMinimumHeight(500))
        self.searchbar_2.editingFinished.connect(lambda: self.search_box_2.setMinimumHeight(100))
        self.searchbar.textChanged.connect(lambda: self.search_box.setMinimumHeight(500))
        self.searchbar.editingFinished.connect(lambda: self.search_box.setMinimumHeight(100))
        self.auto_queue_model.rowsInserted.connect(self.auto_queue_model.itemData)
        self.lock_browser.clicked.connect(self.browsers[self.current_browser].fixPos)
        # self.test.clicked.connect(lambda: self.anynomyzify())
        self.auto_2.stateChanged.connect(self.auto_2_btn)

        # Executed on excel.load
        self.df = self.analysis_excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.analysis_excel.incomplete(self.df, self.cell_selector_start, len(self.df.columns))
        self.populate_sidebar()
        
        self.df_2 = self.testing_excel.load('testing.xlsx', 'Sheet1')
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.testing_excel.incomplete(self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
        self.populate_sidebar_2()

        self.faq_df = self.faq_excel.load('recipes.xlsx', 'Sheet1')
        
        # Initializing FAQ search window item model
        model = QStandardItemModel(len(self.faq_df.index), len(self.faq_df.columns))
        for idx, _ in self.faq_df.iterrows():
            for i, _ in enumerate(self.faq_df.columns):
                item = QStandardItem(self.faq_df.iloc[idx,i])
                model.setItem(idx, i, item) # check this
        self.faq_auto_search_model = QSortFilterProxyModel()
        self.faq_auto_search_model.setSourceModel(model)
        self.faq_auto_search_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.faq_auto_search_model.setFilterKeyColumn(-1) # add this to method 
        self.search_box.installEventFilter(self)
        self.search_box_2.installEventFilter(self)

        # Adding search box
        self.populate_search_column_select()
        self.populate_search_column_select_2()
        self.search_box.setModel(self.faq_auto_search_model)
        self.search_box_2.setModel(self.faq_auto_search_model)
        self.searchbar.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.searchbar_2.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.search_column_select.currentIndexChanged.connect(self.populate_search_box)
        self.search_column_select_2.currentIndexChanged.connect(self.populate_search_box)
        self.populate_search_box()

        # Methods to be executed on startup
        self.populate_canned()
        self.populate_canned_2()
        self.populate_flows(example_flows)
        self.populate_actions(example_actions)

        '''Sets sidebar to first item selected on startup'''
        # index = self.sidebar.model().index(0, 0)
        # self.sidebar.selectionModel().select(
        #     index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

        self.populate_status_bar(2, 0, 2)
        self.populate_cell_selector(self.cell_selector_start, self.header_len+1)
        self.populate_cell_selector_2(self.cell_selector_start_2, self.header_len_2+1)
        

        # Tests
        # print(xw.books.active.name)

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
        self.df = self.analysis_excel.reload()
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.analysis_excel.incomplete(self.df, self.cell_selector_start, len(self.df.columns))
        self.populate_sidebar()

        # Loading web page, web scraping and adding results to self.chat
        if self.open_links.checkState():
            # Start a new thread to load the chat log
            setup = Worker(self.getChatlog, 'activate_output')
            setup.signals.output.connect(self.populate_chat)
            self.threadpool.start(setup)

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
            self.analysis_excel.updateCells(customer, self.row + 2, 5)
            self.analysis_excel.updateCells(bot, self.row + 2, 6)
        
        # Saving analysis contents
        self.analysis_excel.updateCells(self.df.iloc[self.row:self.row+1, 
            self.cell_selector_start:self.header_len].values, 
            self.row + 2, self.cell_selector_start + 1)

        # Saves the excel file
        self.analysis_excel.saveWB()

    def eventFilter(self, source, event):
        '''
        Filters Events and calls the respective functions
        '''
        # Resizing chat message textedits
        if event.type() == event.Resize:
            if self.stackedWidget.currentIndex() == 0:
                QTimer.singleShot(0, self.chat.resizeRowsToContents)
            else:
                QTimer.singleShot(0, self.chat_2.resizeRowsToContents)

        # Show FAQ search table
        if source.objectName() == 'search_box' or source.objectName() == 'search_box_2':
            # print(event.type())
            if event.type() == 82:
                if self.stackedWidget.currentIndex() == 0:
                    index = self.search_box.selectionModel().currentIndex()
                    value = index.sibling(index.row(),index.column()).data()
                else:
                    index = self.search_box_2.selectionModel().currentIndex()
                    value = index.sibling(index.row(),index.column()).data()
                self.faq_auto_search = FaqAutoSearch(self, value=value)

        # Right click to select chat messages
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                if self.stackedWidget.currentIndex() == 0:
                    QTimer.singleShot(0, lambda x=event, y=source: self.select_chat(x, y))
                else:
                    QTimer.singleShot(0, lambda x=event, y=source: self.select_chat_2(x, y))

        # Delete items from Auto Queue
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                indices = self.auto_queue.selectionModel().selectedRows() 
                for index in sorted(indices):
                    self.auto_queue_model.removeRow(index.row())

        # Tab analysis editor
        if source.objectName() == 'analysis':
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Tab:
                    self.btn_right()
                    return True

        # Tab analysis editor 2     
        if source.objectName() == 'analysis_2':
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Tab:
                    self.btn_right_2()
                    return True

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
    
    def getChatlog(self, output):
        if self.browsers[0].isAlive():
            self.browsers[0].setUp(url=self.df.iloc[self.row, 3])
        else:
            self.browsers[0].getURL(url=self.df.iloc[self.row, 3])
        chat_text = self.browsers[self.current_browser].getCleverbotStatic()
        output.emit(chat_text)
        # self.populate_chat(chat_text)

    def populate_chat(self, chat):
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(chat))
        for idx, sender, in enumerate(chat):
            if sender[0] == 'bot':
                combo = TextEdit(self, objectName=f'bot_{idx}') 
            else:
                combo = TextEdit(self, objectName=f'customer_{idx}') 
            self.chat.setCellWidget(idx, 0, combo)
            
            # Add auto highlighting
            if sender[0] == 'customer':
                self.highlighters[idx] = Highlighter(document=combo.document(), name=combo)
            
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
        self.anynomyzify()
        
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


    def getChatText(self, export=None):
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
            if export:
                return customer
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
        
    def anynomyzify(self):
        # cursor = self.analysis.textCursor()
        # cursor.setPosition(2)
        # cursor.setPosition(10, QTextCursor.KeepAnchor)
        # self.analysis.setTextCursor(cursor)
        for name, start, end in self.auto_anonymized:
            cursor = name.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            name.setTextCursor(cursor)

    def populate_cell_selector(self, start, end):
        for item in list(self.df.columns.values)[start:end]:
            self.cell_selector.addItem(item)
            
    def populate_analysis(self):
        # '''Bugfix for number only entries on the excel sheet needed. 
        # self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])
        # TypeError: setText(self, str): argument 1 has unexpected type numpy.float64'''
        # print(self.row, 'no1', self.cell_selector.currentIndex() + self.cell_selector_start)
        self.analysis.setPlainText(self.df.loc[self.row][self.cell_selector.currentIndex() \
            + self.cell_selector_start])

    
    def populate_search_column_select(self):
        for item in list(self.faq_df.columns.values):
            self.search_column_select.addItem(item)
  

    def populate_search_box(self):
        '''
        Populates the search box with values from FAQ excel sheet
        '''
        page = self.stackedWidget.currentIndex()
        if page == 0:
            index = self.search_column_select.currentIndex()
        else:
            index = self.search_column_select_2.currentIndex()
        # Set table column to filter by
        self.faq_auto_search_model.setFilterKeyColumn(index)
        # Show/hide columns according to current selection
        for i in range(0, len(self.faq_df.index)):
            if i != index:
                self.search_box.hideColumn(i) if page == 0 else self.search_box_2.hideColumn(i)
            else:
                self.search_box.showColumn(i) if page == 0 else self.search_box_2.showColumn(i)
                    

        

    def populate_canned(self):
        '''
        Radiobuttons
        '''
        self.canned.setColumnCount(len(canned_questions) + 1)
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
        if not self.cell_selector.currentIndex() < self.header_len - self.cell_selector_start - 1:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() + 2)
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

    def btn_colorize(self):
        self.analysis_excel.colorize(self.row + 2, self.cell_selector.currentIndex() + self.cell_selector_start + 1)

    def switchToAnalysis(self):
        self.is_webscraping = False
        self.stackedWidget.setCurrentWidget(self.analysis_suite)
        self.populate_search_box()

    def switchToTesting(self):
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()

    def exportToTesting(self):
        customer= self.getChatText(export=1)
        if customer:
            for message in customer:
                item = QtGui.QStandardItem(message.lstrip())
                self.auto_queue_model.appendRow(item)
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()
        
    def btn_test(self):
        pass

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
        self.chat_2.setRowCount(0)
        self.marked_messages_2 = []

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row_2:
            self.row_2 = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df_2 = self.testing_excel.reload()
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.testing_excel.incomplete(self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
        self.populate_sidebar_2()

        # Autoscrolling to the selection on the sidebar
        self.sidebar_2.scrollToItem(self.sidebar.item(self.row, 0))

        self.populate_canned_2()
        self.populate_analysis_2()

    def saveOnRowChange_2(self):
        '''
        Saves current states to Excel
        '''
        # Saving correct FAQ
        index = self.search_box_2.selectionModel().currentIndex()
        value = index.sibling(index.row(),index.column()).data()
        if value:
            self.testing_excel.updateCells(value, self.row_2 + 2, 2)

        # Saving canned_2 states
        # print(self.canned_states_2)

        # Saving chat messages
        print(len(self.marked_messages_2))
        if len(self.marked_messages_2) > 0:
            customer, bot = self.getChatText_2()
            self.testing_excel.updateCells(customer, self.row_2 + 2, 3)
            self.testing_excel.updateCells(bot, self.row_2 + 2, 4)
        
        # Saving analysis contents
        self.testing_excel.updateCells(self.df_2.iloc[self.row_2:self.row_2+1, 
            self.cell_selector_start_2:self.header_len_2].values, 
            self.row_2 + 2, self.cell_selector_start_2 + 1)

        # Saves the excel file
        self.testing_excel.saveWB() 

    def save_analysis_2(self):
        '''
        Saves current analysis text to dataframe
        '''
        self.df_2.loc[self.row_2][self.cell_selector_2.currentText()] = self.analysis_2.toPlainText()
    
    def setUpNewDialog(self, browser_num = None):
        '''
        Sets up (singular) new chat session
        '''
        self.browsers[self.current_browser].setUp(url=self.livechat_url)
        self.browsers[self.current_browser].clickCleverbotAgree()
        # clear chat
        self.dialog_num += 1
        self.chat_2.clear()
        self.chat_2.setRowCount(0)
        self.chat_test = []
        return

    def setUpNewAutoDialog(self, i):
        '''
        Prebuffers browser windows and asks auto_queue questions
        '''
        self.browsers[i].setUp(url=self.livechat_url)
        self.browsers[i].clickCleverbotAgree()
        self.browsers[i].prebufferAutoTab(self.questions)

    def initializeWebscraping(self):
        '''
        Start new webscraping thread
        '''
        # Check if there is a running webscraping thread
        if not self.is_webscraping:
            self.is_webscraping = True
            # Pass the function to execute
            live_webscraper = Worker(self.chatWebscrapingLoop, 'activate_output')
            # Catch signal of new chat messages
            live_webscraper.signals.output.connect(self.populate_chat_2)
            # Execute
            self.threadpool.start(live_webscraper)

    def chatWebscrapingLoop(self, output):
        '''
        Continuously fetches new messages from the chat page
        '''
        while self.is_webscraping:
            try:
                chats = self.browsers[self.current_browser].getCleverbotLive()
                output.emit(chats)
                time.sleep(3)
            except:
                time.sleep(3)
                continue

    def populate_chat_2(self, chat):
        output = []
        [output.append(message) for message in chat if message not in self.chat_test and '' not in message]
        self.chat_2.setColumnCount(1)
        length = len(self.chat_test)
        self.chat_2.setRowCount(length + len(output))
        for idx, sender, in enumerate(output, start=length):
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
        [self.chat_test.append(message) for message in output]
        self.chat_2.installEventFilter(self)
        self.chat_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        

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
            [message_cells.append(message.split('_')) for message in self.marked_messages_2]
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


    def populate_cell_selector_2(self, start, end):
        for item in list(self.df_2.columns.values)[start:end]:
            self.cell_selector_2.addItem(item)


    def populate_analysis_2(self):
        # '''Bugfix for number only entries on the excel sheet needed. 
        # self.analysis.setText(self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])
        # TypeError: setText(self, str): argument 1 has unexpected type numpy.float64'''
        # print(self.row_2, self.cell_selector_2.currentIndex() + self.cell_selector_start_2)
        # print(self.df.head)
        # self.analysis_2.setText(self.df_2.loc[1][3])
        self.analysis_2.setText(self.df_2.loc[self.row_2][self.cell_selector_2.currentIndex() + self.cell_selector_start_2])

    
    def populate_search_column_select_2(self):
        for item in list(self.faq_df.columns.values):
            self.search_column_select_2.addItem(item)

    def populate_canned_2(self):
        # Radiobuttons
        self.canned_2.setColumnCount(len(canned_questions )+1)
        self.canned_2.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned_2.setItem(idx, 0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName=f'rb_group_2_{idx}')
            oname = f'rb_group_2_{idx}'
            rb_group.idReleased.connect(self.canned_selection_2)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                # combo.setId(i)
                if self.row_2 in self.canned_states_2:
                    if oname in self.canned_states_2[self.row]:
                        if self.canned_states_2[self.row_2][oname] == choice:
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

    '''Unused'''
    # def populateAutoQueue(self, input):
    #     for row in input:
    #         self.auto_queue_model.appendRow(row)

    # def resetAutoQueueColors(self, index, column, row):
    #     print(column,row, self.auto_queue_model.rowCount())
    #     for row in range(0, self.auto_queue_model.rowCount()):
    #         item = self.auto_queue_model.item(row, 0)
    #         if item:
    #             item.setBackground(QtGui.QColor(70, 70, 70))

    def populateHistory(self, input):
        item = QtGui.QStandardItem(input)
        if self.dialog_num % 2 == 0:
            item.setBackground(QColor(70, 81, 70))
        else:
            item.setBackground(QColor(74, 69, 78))
        self.history_model.appendRow(item)



  
    # def populate_status_bar_2(self, row, start, end):
    #     self.status_bar_2.setText(self.df_2.iloc[row:row+1, start:end+1].to_string(header=False, index=False))


    ################################################################################################
    # Buttons_2
    ################################################################################################

    def send_btn(self):
        '''
        Sends chat messages
        '''
        input = self.chat_input.text()
        if input:
            self.browsers[self.current_browser].setCleverbotLive(input)
            self.populateHistory(input)
            self.chat_input.clear()

    def new_dialog_btn(self):
        '''
        Sets up webscraper, clears dialog and opens new dialog
        '''
        if self.auto_2.checkState():
            current = self.current_browser
            if self.current_browser >= self.buffer_len:
                self.current_browser = 0
            else:
                self.current_browser = self.current_browser + 1
            self.browsers[self.current_browser].bringToFront()
            # Start prebuffering previous window 
            setup = Worker(lambda: self.setUpNewAutoDialog(current))
            self.threadpool.start(setup)
            # clear chat
            self.chat_2.clear()
            self.chat_2.setRowCount(0)
            self.chat_test = []
            # start webscraping current browser window
            if not self.is_webscraping:
                self.initializeWebscraping()
        else:
            # Start Thread for webdriver setup
            setup = Worker(self.setUpNewDialog)
            # Once setup is complete, start webscraping the chat log
            setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)


    def auto_2_btn(self, signal):
        '''
        Turns on auto prebuffering of tabs
        '''
        # If auto is on
        if signal == 2:
            self.is_webscraping = False
            # self.buffering = True
            self.questions = []

            try:
            # Get current questions in auto_queue
                for i in range(0, self.auto_queue_model.rowCount()):
                    index = self.auto_queue_model.index(i, 0)
                    self.questions.append(index.sibling(index.row(),index.column()).data())
            except:
                traceback.print_exc()
                return

            if self.questions != []:
                # Set up three new browser windows and ask the questions in the auto_queue
                for i in range(0, self.buffer_len):
                    setup = Worker(lambda: self.setUpNewAutoDialog(i))
                    self.threadpool.start(setup)
                    print(f'setting up {i}')
            print('setup done')
            if not self.is_webscraping:
                self.initializeWebscraping()

        if signal == 0:
            # If auto is disabled, close browser windows
            # self.buffering = False
            self.is_webscraping = False
            for i in range(0, self.buffer_len):
                self.browsers[i].tearDown()



    def next_btn(self):
        '''
        Loads the next message in the auto_queue into the input box
        '''
        # Get value of the currently selected item in the auto_queue
        index = self.auto_queue.selectionModel().currentIndex()
        value = index.sibling(index.row(),index.column()).data()
        self.chat_input.setText(value)

        # Jumping to next row in line
        self.auto_queue.selectionModel().select(index, QItemSelectionModel.Deselect)
        index = index.row() + 1
        self.auto_queue.selectRow(index)

        # Jump back to the beginning
        if self.auto_queue.selectedIndexes() == []:
            self.auto_queue.selectRow(0)


    def btn_left_2(self):
        if self.cell_selector_2.currentIndex() > 0:
            self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() - 1)

    def btn_right_2(self):
        if not self.cell_selector_2.currentIndex() < self.header_len_2 - self.cell_selector_start_2 - 1:
            self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() + 2)
        self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() + 1)

    def btn_up_2(self):
        if self.row_2 > 0:
            index = self.sidebar_2.model().index(self.row_2 - 1, 0)
            self.sidebar_2.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_down_2(self):
        if self.row_2 < self.index_len_2:
            index = self.sidebar_2.model().index(self.row_2 + 1, 0)
            self.sidebar_2.selectionModel().select(
                index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

    def btn_save_2(self):
        self.saveOnRowChange_2()

    def btn_colorize_2(self):
        '''
        Gives new dialogs a different color in the history table view
        '''
        self.testing_excel.colorize(self.row_2 + 2, self.cell_selector_2.currentIndex() + self.cell_selector_start_2 + 1)

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
