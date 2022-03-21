import sys
import traceback
from PyQt5.QtCore import (
    QEvent,
    QItemSelectionModel,
    Qt,
    QObject,
    pyqtSignal,
    pyqtSlot,
    QThreadPool,
    QSortFilterProxyModel,
    QTimer,
)
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QWidget,
    QGridLayout,
    QMainWindow,
    QHeaderView,
    QTableWidgetItem,
    QButtonGroup,
    QRadioButton,
    QApplication,
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QFont,
    QFontDatabase,
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt5 import QtCore, QtGui, QtWidgets
from qtstylish import qtstylish

from utils.selenium_helpers import Browser
from utils.worker_thread import Worker
from widgets.base_suite import BaseSuite
from utils.data_variables import Data


class TestingSuite(BaseSuite):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        #####################################################
        """Initializing variables"""
        #####################################################

        self.browsers = [Browser() for i in range(0, Data.BUFFER)]
        # Breaks the buffering loop
        self.buffering = False
        self.is_webscraping = False
        self.current_browser = 0

        self.questions = []
        self.dialog_num = 0
        self.sent_messages = []
        self.auto_anonymized = []

        #####################################################
        """Seting up components"""
        #####################################################

        self.setObjectName("testing_suite")

        # This holds the chat input lineedit and the Send / Next / New Dialog buttons
        self.toolbar_container = QWidget(self)
        self.toolbar_layout = QtWidgets.QHBoxLayout(self.toolbar_container)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setObjectName("toolbar_layout")
        self.auto = QtWidgets.QCheckBox()
        self.auto.setMinimumSize(QtCore.QSize(60, 0))
        self.auto.setMaximumSize(QtCore.QSize(60, 16777215))
        self.auto.setObjectName("auto")
        self.toolbar_layout.addWidget(self.auto)
        self.chat_input = QtWidgets.QLineEdit()
        self.chat_input.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.chat_input.setFont(font)
        self.chat_input.setObjectName("chat_input")
        self.toolbar_layout.addWidget(self.chat_input)
        self.send = QtWidgets.QPushButton()
        self.send.setMaximumSize(QtCore.QSize(70, 16777215))
        self.send.setObjectName("send")
        self.toolbar_layout.addWidget(self.send)
        self.next_question = QtWidgets.QPushButton()
        self.next_question.setMaximumSize(QtCore.QSize(70, 16777215))
        self.next_question.setObjectName("next_question")
        self.toolbar_layout.addWidget(self.next_question)
        self.new_dialog = QtWidgets.QPushButton()
        self.new_dialog.setMinimumSize(QtCore.QSize(90, 0))
        self.new_dialog.setMaximumSize(QtCore.QSize(80, 16777215))
        self.new_dialog.setObjectName("new_dialog")
        self.toolbar_layout.addWidget(self.new_dialog)
        self.auto.setText("Auto")
        self.chat_input.setPlaceholderText("Send")
        self.send.setText("Send")
        self.next_question.setText("Next")
        self.new_dialog.setText("New Dialog")
        self.dataframe_chat_grid.addWidget(self.toolbar_container, 1, 0)

        self.chat_input.returnPressed.connect(self.send_btn)
        self.send.clicked.connect(self.send_btn)
        self.new_dialog.clicked.connect(self.new_dialog_btn)
        self.next_question.clicked.connect(self.next_btn)
        self.auto.stateChanged.connect(self.auto_btn)
        # self.test.clicked.connect(self.btn_test)
        # self.lock_browser.clicked.connect(self.browsers[self.current_browser].fixPos)

    def send_btn(self):
        """
        Sends chat messages
        """
        input = self.chat_input.text()
        if input:
            self.browsers[self.current_browser].setCleverbotLive(input)
            self.populateHistory(input)
            self.chat_input.clear()

    def new_dialog_btn(self):
        """
        Sets up webscraper, clears dialog and opens new dialog
        """
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
            self.sent_messages = []
        else:
            # Start Thread for webdriver setup
            setup = Worker(self.setUpNewDialog)
            # Once setup is complete, start webscraping the chat log
            if not self.is_webscraping:
                setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)

    def auto_2_btn(self, signal):
        """
        Turns on auto prebuffering of tabs
        """
        # If auto is on
        if signal == 2:
            self.questions = []

            try:
                # Get current questions in auto_queue
                for i in range(0, self.auto_queue_model.rowCount()):
                    index = self.auto_queue_model.index(i, 0)
                    self.questions.append(
                        index.sibling(index.row(), index.column()).data()
                    )
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
                    print(f"setting up {i}")
            print("setup done")

        if signal == 0:
            # If auto is disabled, close browser windows
            self.is_webscraping = False
            for i in range(0, self.buffer_len):
                setup = Worker(lambda: self.browsers[i].tearDown())
                self.threadpool.start(setup)

    def next_btn(self):
        """
        Loads the next message in the auto_queue into the input box
        """
        # Get value of the currently selected item in the auto_queue
        index = self.auto_queue.selectionModel().currentIndex()
        value = index.sibling(index.row(), index.column()).data()
        self.chat_input.setText(value)

        # Jumping to next row in line
        self.auto_queue.selectionModel().select(index, QItemSelectionModel.Deselect)
        index = index.row() + 1
        self.auto_queue.selectRow(index)

        # Jump back to the beginning
        if self.auto_queue.selectedIndexes() == []:
            self.auto_queue.selectRow(0)

    def switchToAnalysis(self):
        self.is_webscraping = False
        self.stackedWidget.setCurrentWidget(self.analysis_suite)
        self.populate_search_box()
