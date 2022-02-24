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
from excel_helpers import Excel 
from selenium_helpers import Browser
from data_variables import *
from stylesheets import Stylesheets
from bs4 import BeautifulSoup  
import qtstylish

# PandasGUI imports
import inspect
import os
import pprint
from typing import Callable, Union
from dataclasses import dataclass
import pandas as pd
import pkg_resources
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import pandasgui
from pandasgui.store import PandasGuiStore
from pandasgui.utility import as_dict, fix_ipython, get_figure_type, resize_widget
from pandasgui.widgets.find_toolbar import FindToolbar
from pandasgui.widgets.json_viewer import JsonViewer
from pandasgui.widgets.navigator import Navigator
from pandasgui.widgets.figure_viewer import FigureViewer
from pandasgui.widgets.settings_editor import SettingsEditor
from pandasgui.widgets.python_highlighter import PythonHighlighter
from IPython.core.magic import register_line_magic
import logging


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

class BackgroundRemover(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self.itemData)
    
    def itemData(self, item):
        # print(item.index())
        roles = super().itemData(item.index())
        if 8 in roles:
            del roles[8]
            return super().itemData(item.index())
            return roles
            print(roles)

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
        pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+" # Working changes
        # pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" # Original
        self.add_mapping(pattern, class_format)
        
        # Phone numbers
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
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
    Custom implementation for auto resizing text edits in tables 
    and keeping track of user selected messages
    '''
    def __init__(self, *args, participant, index, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.updateGeometry)
        self.participant = participant
        self.index = index
        self.selected = False
        
    # Handles setting style change when user selects a message 
    # as well as setting the selection status.
    def setSelection(self):
        if self.selected:
            self.selected = False
            if self.participant == 'bot':
                 self.setStyleSheet(Stylesheets.bot)
            else:
                self.setStyleSheet(Stylesheets.customer)
        else:
            self.selected = True
            if self.participant == 'bot':
                self.setStyleSheet(Stylesheets.bot_selected)
            else:
                self.setStyleSheet(Stylesheets.customer_selected)
        
    def __str__(self):
        return self.toHtml()

    def sizeHint(self):
        # Auto resizing text editors
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

class AddVariant(QWidget):
    '''
    Adds FAQ variant questions to the FAQ database
    '''
    def __init__(self, parent=None, text_input=None):
        super(AddVariant, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("Add Variant")
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.variant = QTextEdit(objectName='variant_text')
        self.variant.setText(text_input)
        self.variant.setStyleSheet(
                    'font-size: 11pt; \
                    border-style: outset; \
                    border-left-width: 5px; \
                    border-left-color: rgb(83, 43, 114); \
                    padding-left: 4px; \
                    background-color: rgb(90, 90, 90);')
        self.variant.installEventFilter(self)
        self.variant.setMinimumWidth(700)
        
        add_variant = QPushButton(
            text='Add Variant', objectName='add_variant')        
        self.cancel_variant = QPushButton(
            text='Cancel', objectName='cancel_add_variant')        
        self.cancel_variant.clicked.connect(self.close)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.variant, 0, 0, 1, 2)
        self.layout.addWidget(add_variant, 1, 0, 1, 1)
        self.layout.addWidget(self.cancel_variant, 1, 1, 1, 1)
        self.setLayout(self.layout)
        self.setStyleSheet(Stylesheets.elegantdark)
        self.show()


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
        self.buffer_len = 3

        # Instantiating classes
        self.threadpool = QThreadPool()
        self.is_webscraping = False
        self.analysis_excel = Excel()
        self.testing_excel = Excel()
        self.faq_excel = Excel()
        self.browsers = [Browser() for i in range(0, self.buffer_len + 1)]

        # Breaks the buffering loop
        self.buffering = False
        
        self.current_browser = 0
        self.questions = []
        self.highlighters = {}
        self.row = 0
        self.row_2 = 0
        # Stores what view the user has worked in last
        self.workingViewNum = 0
        self.header_len = 0
        self.header_len_2 = 0
        self.index_len = 0
        self.index_len_2 = 0
        self.dialog_num = 0
        self.canned_states = {}
        self.canned_states_2 = {}
        self.marked_messages = {}
        self.marked_messages_2 = {}
        self.chat_test = []
        self.filter_proxy_model = ''
        self.auto_anonymized = []

        # Load Ui file, set settings
        loadUi('main_window.ui', self)
        self.setWindowTitle('Content Engineer Studio')
        self.setContentsMargins(0, 0, 0, 0)
        
        # Set analysis and testing splitter stretch
        sizes = [99999, 1]
        self.splitter_5.setSizes(sizes)
        self.splitter_2.setSizes(sizes)

        # Apply custom stylesheets
        self.setStyleSheet(Stylesheets.custom_dark)
        # self.colorize_2.setStyleSheet(style_colorize_2)
        # self.setStyleSheet(style_QLineEdit)
                    
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
        self.auto_queue_model = BackgroundRemover()
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
        self.searchbar.textChanged.connect(lambda: self.search_box.setMinimumHeight(500))
        self.searchbar.editingFinished.connect(lambda: self.search_box.setMinimumHeight(100))
        self.searchbar_2.textChanged.connect(lambda: self.search_box_2.setMinimumHeight(500))
        self.searchbar_2.editingFinished.connect(lambda: self.search_box_2.setMinimumHeight(100))
        self.lock_browser.clicked.connect(self.browsers[self.current_browser].fixPos)
        self.auto_2.stateChanged.connect(self.auto_2_btn)
        self.clear.clicked.connect(lambda: self.auto_queue_model.clear())
        self.stackedWidget.currentChanged.connect(self.workingView)
        self.close_faq.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(self.workingViewNum))
        self.close_settings.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(self.workingViewNum))
        self.close_excel.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(self.workingViewNum))
        self.analysis_menu.triggered.connect(self.switchToAnalysis)
        self.testing_menu.triggered.connect(self.switchToTesting)
        self.faq_menu.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.settings_menu_2.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.data_frame_viewer_menu.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(5))
        # self.auto_queue_model.rowsInserted.connect(self.auto_queue_model.itemData)
        self.test.clicked.connect(self.btn_test)

        # Executed on excel.load
        self.df = self.analysis_excel.load('transcripts.xlsx', 'Sheet1')
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.analysis_excel.incomplete(self.df, self.cell_selector_start, len(self.df.columns))
        self.populate_sidebar()
        

        
        self.df_2 = self.testing_excel.load('testing.xlsx', 'Sheet1')
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.testing_excel.incomplete(
            self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
        self.populate_sidebar_2()

        self.faq_df = self.faq_excel.load('recipes.xlsx', 'Sheet1')
        
        # Adding PandasGUI
        '''
        Start PandasGUI init
        Provides a viewer and editor for dataframes
        https://github.com/adrotog/PandasGUI
        '''
        logger = logging.getLogger(__name__)

        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)
        
        # Set the exception hook to our wrapping function
        sys.excepthook = except_hook

        # Enables PyQt event loop in IPython
        fix_ipython()

        # Keep a list of widgets so they don't get garbage collected
        self.refs = []       
        
        '''Start show'''
        settings = {}
        
        # Register IPython magic
        # try:
        #     @register_line_magic
        #     def pg(line):
        #         pandas_gui.store.eval_magic(line)
        #         return line

        # except Exception as e:
        #     # Let this silently fail if no IPython console exists
        #     if e.args[0] == 'Decorator can only run in context where `get_ipython` exists':
        #         pass
        #     else:
        #         raise e
        
        '''Start viewer init'''
        self.navigator = None
        self.splitter = None
        self.find_bar = None
        
        self.refs.append(self)
        
        self.store = PandasGuiStore()
        self.store.gui = self
        
        # Add user provided settings to data store
        for key, value in settings.items():
            setting = self.store.settings[key]
            setting.value = value

        self.code_history_viewer = None
        
        '''Create all widgets'''
        # Hide the question mark on dialogs
        # self.app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        
        # Accept drops, for importing files. See methods below: dropEvent, dragEnterEvent, dragMoveEvent
        self.setAcceptDrops(True)

        # This holds the DataFrameExplorer for each DataFrame
        self.stacked_widget = QtWidgets.QStackedWidget()
        
        # Make the navigation bar
        self.navigator = Navigator(self.store)

        # Make splitter to hold nav and DataFrameExplorers
        self.splitter = QtWidgets.QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.navigator)
        self.splitter.addWidget(self.stacked_widget)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        
        '''Addin to main_window'''
        self.verticalLayout_2.addWidget(self.splitter)

        # makes the find toolbar
        self.find_bar = FindToolbar(self)
        self.addToolBar(self.find_bar)
        
        # Create a copy of the settings in case the SettingsStore reference has
        # been discarded by Qt prematurely
        # https://stackoverflow.com/a/17935694/10342097
        # self.store.settings = self.store.settings.copy()
        
        # Signals
        self.store.settings.settingsChanged.connect(self.apply_settings)

        self.apply_settings()
        
        '''Continue init'''
        dataframe_kwargs = {'Analysis':self.df, 'Testing':self.df_2}
        for df_name, df in dataframe_kwargs.items():
            self.store.add_dataframe(df, df_name)

        # Default to first item
        self.navigator.setCurrentItem(self.navigator.topLevelItem(0))
        
        '''Add  to menubar'''
        @dataclass
        class MenuItem:
            name: str
            func: Callable
            shortcut: str = ''

        items = {'Edit': [MenuItem(name='Find',
                                   func=self.find_bar.show_find_bar,
                                   shortcut='Ctrl+F'),
                          MenuItem(name='Copy',
                                   func=self.copy,
                                   shortcut='Ctrl+C'),
                          MenuItem(name='Copy With Headers',
                                   func=self.copy_with_headers,
                                   shortcut='Ctrl+Shift+C'),
                          MenuItem(name='Paste',
                                   func=self.paste,
                                   shortcut='Ctrl+V'),
                          MenuItem(name='Import',
                                   func=self.import_dialog),
                          MenuItem(name='Import From Clipboard',
                                   func=self.import_from_clipboard),
                          MenuItem(name='Export',
                                   func=self.export_dialog),
                          MenuItem(name='Code Export',
                                   func=self.show_code_export),
                          ],
                 'DataFrame': [MenuItem(name='Delete Selected DataFrames',
                                        func=self.delete_selected_dataframes),
                               MenuItem(name='Reload DataFrames',
                                        func=self.reload_data,
                                        shortcut='Ctrl+R'),
                               MenuItem(name='Parse All Dates',
                                        func=lambda: self.store.selected_pgdf.parse_all_dates()),
                               ],
                 'Settings': [MenuItem(name='Preferences...',
                                       func=self.edit_settings),
                              {"Context Menus": [MenuItem(name='Add PandasGUI To Context Menu',
                                                          func=self.add_to_context_menu),
                                                 MenuItem(name='Remove PandasGUI From Context Menu',
                                                          func=self.remove_from_context_menu),
                                                 MenuItem(name='Add JupyterLab To Context Menu',
                                                          func=self.add_jupyter_to_context_menu),
                                                 MenuItem(name='Remove JupyterLab From Context Menu',
                                                          func=self.remove_jupyter_from_context_menu), ]}

                              ],
                 'Debug': [MenuItem(name='About',
                                    func=self.about),
                           MenuItem(name='Browse Sample Datasets',
                                    func=self.show_sample_datasets),
                           MenuItem(name='View PandasGuiStore',
                                    func=self.view_store),
                           MenuItem(name='View DataFrame History',
                                    func=self.view_history),
                           ]
                 }
        
        def add_menus(dic, root):
            # Add menu items and actions to UI using the schema defined above
            for menu_name in dic.keys():
                menu = root.addMenu(menu_name)
                for x in dic[menu_name]:
                    if type(x) == dict:
                        add_menus(x, menu)
                    else:
                        action = QtWidgets.QAction(x.name, self)
                        action.setShortcut(x.shortcut)
                        action.triggered.connect(x.func)
                        menu.addAction(action)

        add_menus(items, self.menubar)
        
        '''End PandasGUI init'''
        
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
        self.search_box_3.installEventFilter(self)

        # Adding search box
        self.populate_search_column_select()
        self.search_box.setModel(self.faq_auto_search_model)
        self.search_box_2.setModel(self.faq_auto_search_model)
        self.search_box_3.setModel(self.faq_auto_search_model)
        self.search_box_3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.searchbar.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.searchbar_2.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.searchbar_3.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.search_column_select.currentIndexChanged.connect(self.populate_search_box)
        self.search_column_select_2.currentIndexChanged.connect(self.populate_search_box)
        self.search_column_select_3.currentIndexChanged.connect(self.populate_search_box)
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
    PandasGUI Methods
    '''
    ################################################################################################
    def apply_settings(self):
        theme = self.store.settings.theme.value
        if theme == "classic":
            self.setStyleSheet("")
            self.store.settings.theme.value = 'classic'
        elif theme == "dark":
            self.setStyleSheet(qtstylish.dark())
            self.store.settings.theme.value = 'dark'
        elif theme == "light":
            self.setStyleSheet(qtstylish.light())
            self.store.settings.theme.value = 'light'

    def copy(self):
        if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
            self.store.selected_pgdf.dataframe_explorer.dataframe_viewer.copy()
        elif self.store.selected_pgdf.dataframe_explorer.active_tab == "Statistics":
            self.store.selected_pgdf.dataframe_explorer.statistics_viewer.dataframe_viewer.copy()

    def copy_with_headers(self):
        if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
            self.store.selected_pgdf.dataframe_viewer.copy(header=True)
        elif self.store.selected_pgdf.dataframe_explorer.active_tab == "Statistics":
            self.store.selected_pgdf.dataframe_explorer.statistics_viewer.dataframe_viewer.copy(header=True)

    def paste(self):
        if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
            self.store.selected_pgdf.dataframe_explorer.dataframe_viewer.paste()

    def show_code_export(self):
        self.store.selected_pgdf.dataframe_explorer.code_history_viewer.show()

    def update_code_export(self):
        self.store.selected_pgdf.dataframe_explorer.code_history_viewer.refresh()


    def delete_selected_dataframes(self):
        for name in [item.text(0) for item in self.navigator.selectedItems()]:
            self.store.remove_dataframe(name)

    def reorder_columns(self):
        self.store.selected_pgdf

    def dropEvent(self, e):
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            fpath_list = []
            for url in e.mimeData().urls():
                fpath_list.append(str(url.toLocalFile()))

            for fpath in fpath_list:
                self.store.import_file(fpath)
        else:
            e.ignore()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def view_history(self):
        d = self.store.selected_pgdf.history
        self.viewer = JsonViewer(d)
        self.viewer.show()

    def view_store(self):
        d = as_dict(self.store)
        self.viewer = JsonViewer(d)
        self.viewer.show()

    # Return all DataFrames, or a subset specified by names. 
    # Returns a dict of name:df or a single df if there's only 1
    def get_dataframes(self, names: Union[None, str, list] = None):
        return self.store.get_dataframes(names)

    def __getitem__(self, key):
        return self.get_dataframes(key)

    def import_dialog(self):
        dialog = QtWidgets.QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter="*.csv *.xlsx *.parquet *.json")
        for path in paths:
            self.store.import_file(path)

    def export_dialog(self):
        dialog = QtWidgets.QFileDialog()
        pgdf = self.store.selected_pgdf
        path, _ = dialog.getSaveFileName(directory=pgdf.name, filter="*.csv")
        if path:
            pgdf.df.to_csv(path, index=False)

    def import_from_clipboard(self):
        df = pd.read_clipboard(sep=',|\t', engine="python",
                               na_values='""',  # https://stackoverflow.com/a/67915100/3620725
                               skip_blank_lines=False)
        self.store.add_dataframe(df)

    # https://stackoverflow.com/a/29769228/3620725
    def add_to_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        command_value = rf'{sys.executable} -m pandasgui.run_with_args "%V"'
        icon_value = fr"{os.path.dirname(pandasgui.__file__)}\resources\images\icon.ico"

        handle = winreg.CreateKeyEx(key, "Software\Classes\*\shell\Open with PandasGUI\command", 0,
                                    winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "", 0, winreg.REG_SZ, command_value)
        handle = winreg.CreateKeyEx(key, "Software\Classes\*\shell\Open with PandasGUI", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "icon", 0, winreg.REG_SZ, icon_value)

    def remove_from_context_menu(self):
        import winreg
        key = winreg.HKEY_CURRENT_USER
        winreg.DeleteKey(key, "Software\Classes\*\shell\Open with PandasGUI\command")
        winreg.DeleteKey(key, "Software\Classes\*\shell\Open with PandasGUI")

    def add_jupyter_to_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        command_value = rf'cmd.exe /k jupyter lab --notebook-dir="%V"'
        icon_value = fr"{os.path.dirname(pandasgui.__file__)}\resources\images\jupyter_icon.ico"

        handle = winreg.CreateKeyEx(key, "Software\Classes\directory\Background\shell\Open with JupyterLab\command", 0,
                                    winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "", 0, winreg.REG_SZ, command_value)
        handle = winreg.CreateKeyEx(key, "Software\Classes\directory\Background\shell\Open with JupyterLab", 0,
                                    winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "icon", 0, winreg.REG_SZ, icon_value)

    def remove_jupyter_from_context_menu(self):
        import winreg
        key = winreg.HKEY_CURRENT_USER
        winreg.DeleteKey(key, "Software\Classes\directory\Background\shell\Open with JupyterLab\command")
        winreg.DeleteKey(key, "Software\Classes\directory\Background\shell\Open with JupyterLab")

    def edit_settings(self):

        dialog = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(SettingsEditor(self.store.settings))
        dialog.setLayout(layout)
        dialog.resize(700, 800)
        dialog.show()

    def about(self):
        import pandasgui
        dialog = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        layout.addWidget(QtWidgets.QLabel(f"Version: {pandasgui.__version__}"))
        layout.addWidget(QtWidgets.QLabel(
            f'''GitHub: <a style="color: #1e81cc;" 
            href="https://github.com/adamerose/PandasGUI">https://github.com/adamerose/PandasGUI</a>'''))
        # dialog.resize(500, 500)
        dialog.setWindowTitle("About")
        dialog.show()

    def show_sample_datasets(self):
        from pandasgui.datasets import LOCAL_DATASET_DIR
        import os
        os.startfile(LOCAL_DATASET_DIR, 'explore')

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.refs.remove(self)
        super().closeEvent(e)

    # Replace all GUI DataFrames with the current DataFrame of the same name from the scope show was called
    def reload_data(self):
        callers_local_vars = self.caller_stack.f_locals.items()
        refreshed_names = []
        for var_name, var_val in callers_local_vars:
            for ix, name in enumerate([pgdf.name for pgdf in self.store.data.values()]):
                if var_name == name:
                    none_found_flag = False
                    self.store.remove_dataframe(var_name)
                    self.store.add_dataframe(var_val, name=var_name)
                    refreshed_names.append(var_name)

        if not refreshed_names:
            print("No matching DataFrames found to reload")
        else:
            print(f"Refreshed {', '.join(refreshed_names)}")

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
        self.marked_messages = {}

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row:
            self.row = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df = self.analysis_excel.reload()
        self.header_len = len(self.df.columns)
        self.index_len = len(self.df.index)
        self.completed = self.analysis_excel.incomplete(
            self.df, self.cell_selector_start, len(self.df.columns))
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
        if self.chat.rowCount() > 0:
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
            page = self.stackedWidget.currentIndex()
            if page == 0:
                QTimer.singleShot(0, self.chat.resizeRowsToContents)
            elif page == 1:
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
                self.stackedWidget.setCurrentWidget(self.faq)
                self.searchbar_3.setText(value)
        # Navigate back to working view
        if source.objectName() == 'search_box_3':
            if event.type() == 82:
                index = self.search_box_3.selectionModel().currentIndex()
                value = index.sibling(index.row(),index.column()).data()
                self.search_column_select_3.setCurrentIndex(index.column())
                self.searchbar.setText(value) if self.workingViewNum == 0 else self.searchbar_2.setText(value)
                self.stackedWidget.setCurrentIndex(self.workingViewNum)
                self.populate_search_box()
                self.search_box.setMinimumHeight(100)
                self.search_box_2.setMinimumHeight(100)
                
        # Right click to select chat messages | middle click to add Variants
        if 'bot_' in source.objectName() or 'customer_' in source.objectName():
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.RightButton:
                    source.setSelection()
                # Variants
                if event.button() == Qt.MiddleButton and 'customer' in source.objectName():
                    text = source.toPlainText()
                    self.new_variant = AddVariant(text_input=text)
                    

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
        '''
        Accesses URL and downloads chat log
        '''
        if not self.browsers[0].getURL(url=self.df.iloc[self.row, 3]):
            self.browsers[0].setUp(url=self.df.iloc[self.row, 3])
        chat_text = self.browsers[self.current_browser].getCleverbotStatic()
        output.emit(chat_text)
        # self.populate_chat(chat_text)

    def populate_chat(self, chat):
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(chat))
        for idx, sender, in enumerate(chat):
            if sender[0] == 'bot':
                combo = TextEdit(
                    self, objectName=f'bot_{idx}', 
                    participant='bot', index=idx) 
            else:
                combo = TextEdit(
                    self, objectName=f'customer_{idx}', 
                    participant='customer', index=idx) 
            self.chat.setCellWidget(idx, 0, combo)
            
            # Add auto highlighting
            if sender[0] == 'customer':
                self.highlighters[idx] = Highlighter(document=combo.document(), name=combo)
            
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            
            # Bot
            if sender[0] == 'bot':
                combo.setStyleSheet(Stylesheets.bot)
                # combo.setAlignment(Qt.AlignRight)
                
            # customer
            else:
                combo.setStyleSheet(Stylesheets.customer)
                
            combo.textChanged.connect(lambda idx=idx: self.chat.resizeRowToContents(idx))
            combo.cursorPositionChanged.connect(self.highlight_selection)
        self.chat.installEventFilter(self)
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anynomyzify()
        
    def clearChat(self):
        # self.chat.clear()
        self.chat.setRowCount(0)

    def getChatText(self, export=None):
        '''
        Pulls and anonymizes user selected messages from the chat tablewidget. Returns dict of messages.
        '''
        bot = []
        customer = []
        # Iterate over editors in self.chat TableWidget
        for idx in range(0, self.chat.rowCount()):
            editor = self.chat.cellWidget(idx, 0)
            if editor.selected:
                # Convert the text of the message at the grid location to HTML and parse it
                message_html = BeautifulSoup(str(editor), 'html.parser')
                # Find all span tags and replace the text with ***
                tags = message_html.find_all('span')
                for tag in tags:
                    tag.string = '***'
                if editor.participant == 'bot':
                    bot.append(message_html.get_text().strip())
                else:
                    customer.append(message_html.get_text().strip())
        if export:
                return customer
        return '\n'.join(customer), '\n'.join(bot)


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
        '''
        Receives starting and ending positions 
        of words to select from the Highlighter subclass and selects them
        '''
        for name, start, end in self.auto_anonymized:
            cursor = name.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            name.setTextCursor(cursor)
            # cursor.clearSelection()
        self.auto_anonymized = []

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
        '''
        Set model for FAQ search selector
        '''
        model = QStandardItemModel(len(self.faq_df.columns), 0)
        for idx, item in enumerate(list(self.faq_df.columns.values)):
            item = QStandardItem(item)
            model.setItem(idx, 0, item)
            
        # For searching all columns
        item = QStandardItem('Search in all columns')
        model.setItem(len(self.faq_df.columns), 0, item)
        self.search_column_select.setModel(model)
        self.search_column_select_2.setModel(model)
        self.search_column_select_3.setModel(model)
  

    def populate_search_box(self):
        '''
        Populates the search box with values from FAQ excel sheet
        '''
        # Synchronize selectors
        page = self.stackedWidget.currentIndex()
        if page == 0:
            index = self.search_column_select.currentIndex()
            self.search_column_select_2.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 1:
            index = self.search_column_select_2.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 3:
            index = self.search_column_select_3.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_2.setCurrentIndex(index)
            
        # Set table column to filter by
        try:
            if index == len(self.faq_df.columns):
                # Set to filter by all columns
                self.faq_auto_search_model.setFilterKeyColumn(-1)
            else:
                self.faq_auto_search_model.setFilterKeyColumn(index)
        except UnboundLocalError as e:
            pass
            
        # Show/hide columns according to current selection
        if (page == 0 or page == 1) and index != len(self.faq_df.columns):
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


    def populate_sidebar(self):
        
        self.sidebar.setColumnCount(1)
        self.sidebar.setRowCount(self.index_len)
        [self.sidebar.setItem(idx,0, QTableWidgetItem(str(idx + 2))) for idx in range(0, self.index_len)]
        [self.sidebar.item(idx, 0).setBackground(QtGui.QColor(100, 100, 100)) 
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
        self.analysis_excel.colorize(
            self.row + 2, self.cell_selector.currentIndex() + self.cell_selector_start + 1)

    def switchToAnalysis(self):
        self.is_webscraping = False
        self.stackedWidget.setCurrentWidget(self.analysis_suite)
        self.populate_search_box()

    def switchToTesting(self):
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()

    def exportToTesting(self):
        customer = self.getChatText(export=1)
        if customer:
            for message in customer:
                print(message)
                item = QtGui.QStandardItem(message)
                self.auto_queue_model.appendRow(item)
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()
        
    def workingView(self, idx):
        if idx == 0 | idx == 1:
            self.workingViewNum = idx

        
    def btn_test(self):
        index = self.history_model.index(3, 0)
        # print(index)
        print(self.history_model.itemData(index))


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
        self.marked_messages_2 = {}

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row_2:
            self.row_2 = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df_2 = self.testing_excel.reload()
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.testing_excel.incomplete(
            self.df_2, self.cell_selector_start_2, len(self.df_2.columns))
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
        if self.chat_2.rowCount() > 0:
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
        # self.browsers[i].tearDown()
        if self.browsers[i].setUp(url=self.livechat_url):
            self.browsers[i].clickCleverbotAgree()
            self.browsers[i].prebufferAutoTab(self.questions)
        return

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
                if chats:
                    output.emit(chats)
                time.sleep(5)
            except:
                time.sleep(5)
                continue

    def populate_chat_2(self, chat):
        output = []
        [output.append(message) for message in chat if message not in self.chat_test and '' not in message]
        self.chat_2.setColumnCount(1)
        length = len(self.chat_test)
        self.chat_2.setRowCount(length + len(output))
        for idx, sender, in enumerate(output, start=length):
            if sender[0] == 'bot':
                combo = TextEdit(self, objectName=f'bot_{idx}', participant='bot', index=idx)
            else:
                combo = TextEdit(self, objectName=f'customer_{idx}', participant='customer', index=idx)
            self.chat_2.setCellWidget(idx, 0, combo)
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            # Bot
            if sender[0] == 'bot':
                combo.setStyleSheet(Stylesheets.bot)
            # customer
            else:
                combo.setStyleSheet(Stylesheets.customer)
            combo.textChanged.connect(lambda idx=idx: self.chat_2.resizeRowToContents(idx))
            combo.cursorPositionChanged.connect(self.highlight_selection_2)
        [self.chat_test.append(message) for message in output]
        self.chat_2.installEventFilter(self)
        self.chat_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    

    def getChatText_2(self, export=None):
        '''
        Pulls and anonymizes user selected messages from the chat tablewidget. Returns dict of messages.
        '''
        bot = []
        customer = []
        # Iterate over editors in self.chat TableWidget
        for idx in range(0, self.chat_2.rowCount()):
            editor = self.chat_2.cellWidget(idx, 0)
            if editor.selected:
                message_html = BeautifulSoup(self.chat_2.cellWidget(int(idx), 0).toHtml(), 'html.parser')
                # Find all span tags and replace the text with ***
                tags = message_html.find_all('span')
                for tag in tags:
                    tag.string = '***'
                if editor.participant == 'bot':
                    bot.append(message_html.get_text().strip())
                else:
                    customer.append(message_html.get_text().strip())
            if export:
                return customer
        return '\n'.join(customer), '\n'.join(bot)


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
        # self.analysis.setText(
            # self.df.loc[self.row][self.cell_selector.currentIndex() + self.cell_selector_start])
        # TypeError: setText(self, str): argument 1 has unexpected type numpy.float64'''
        # print(self.row_2, self.cell_selector_2.currentIndex() + self.cell_selector_start_2)
        # print(self.df.head)
        # self.analysis_2.setText(self.df_2.loc[1][3])
        self.analysis_2.setText(
            self.df_2.loc[self.row_2][self.cell_selector_2.currentIndex() + self.cell_selector_start_2])

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
            if self.browsers[self.current_browser] is None:
                self.browsers[self.current_browser] = Browser()
            self.browsers[self.current_browser].bringToFront()
            # Start prebuffering previous window 
            setup = Worker(lambda: self.setUpNewAutoDialog(current))
            if not self.is_webscraping:
                setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)
            # clear chat
            self.chat_2.clear()
            self.chat_2.setRowCount(0)
            self.chat_test = []
        else:
            # Start Thread for webdriver setup
            setup = Worker(self.setUpNewDialog)
            # Once setup is complete, start webscraping the chat log
            if not self.is_webscraping:
                setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)


    def auto_2_btn(self, signal):
        '''
        Turns on auto prebuffering of tabs
        '''
        # If auto is on
        if signal == 2:
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
                
                # Set up self.buffer_len new browser windows and ask the questions in the auto_queue
                for i in range(0, self.buffer_len):
                    setup = Worker(lambda: self.setUpNewAutoDialog(i))
                    if not self.is_webscraping and i == 0:
                        setup.signals.finished.connect(self.initializeWebscraping)
                    self.threadpool.start(setup)
                    print(f'setting up {i}')
            print('setup done')

        if signal == 0:
            # If auto is disabled, close browser windows
            self.is_webscraping = False
            for i in range(0, self.buffer_len):
                setup = Worker(lambda: self.browsers[i].tearDown())
                self.threadpool.start(setup)
                



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
        Applies highlight color to specified cells
        '''
        self.testing_excel.colorize(
            self.row_2 + 2, self.cell_selector_2.currentIndex() + self.cell_selector_start_2 + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    # app.setStyleSheet(elegantdark)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

