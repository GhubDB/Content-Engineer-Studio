import traceback
import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QWidget

from ContentEngineerStudio.data.data_variables import Data
from ContentEngineerStudio.utils.selenium_helpers import Browser
from ContentEngineerStudio.utils.worker_thread import Worker
from ContentEngineerStudio.widgets.auto_history import AutoqueueAndHistoryContainer
from ContentEngineerStudio.widgets.base_suite import BaseSuite


class TestingSuite(BaseSuite):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        #####################################################
        """Initializing variables"""
        #####################################################

        self.browsers = [Browser() for i in range(0, Data.BUFFER)]
        self.viewer = None

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

        self.auto_history = AutoqueueAndHistoryContainer(parent=self)
        self.component_splitter.addWidget(self.auto_history)

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
        input_string = self.chat_input.text()
        if input_string:
            self.browsers[self.current_browser].set_cleverbot_live(input_string)
            self.auto_history.populate_history(input_string)
            self.chat_input.clear()

    def new_dialog_btn(self):
        """
        Sets up webscraper, clears dialog and opens new dialog
        """
        if self.auto.checkState():
            current = self.current_browser
            if self.current_browser >= Data.BUFFER:
                self.current_browser = 0
            else:
                self.current_browser = self.current_browser + 1
            if self.browsers[self.current_browser] is None:
                self.browsers[self.current_browser] = Browser()
            self.browsers[self.current_browser].bring_to_front()
            # Start prebuffering previous window
            setup = Worker(lambda: self.chat.set_up_new_auto_dialog(current))
            if not self.is_webscraping:
                setup.signals.finished.connect(self.chat.initialize_webscraping)
            self.gui.threadpool.start(setup)
            # clear chat
            self.chat.clear_chat()
            self.sent_messages = []
        else:
            # Start Thread for webdriver setup
            setup = Worker(self.chat.set_up_new_dialog)
            # Once setup is complete, start webscraping the chat log
            if not self.is_webscraping:
                setup.signals.finished.connect(self.chat.initialize_webscraping)
            self.gui.threadpool.start(setup)

    def auto_btn(self, signal):
        """
        Turns on auto prebuffering of tabs
        """
        # If auto is on
        if signal == 2:
            self.questions = []

            if self.auto_history.auto_queue_model.rowCount() > 0:
                # Get current questions in auto_queue
                for i in range(0, self.auto_history.auto_queue_model.rowCount()):
                    index = self.auto_history.auto_queue_model.index(i, 0)
                    self.questions.append(
                        index.sibling(index.row(), index.column()).data()
                    )

            if self.questions:

                # Set up Data.BUFFER new browser windows and ask the questions in the auto_queue
                for i in range(0, Data.BUFFER):
                    setup = Worker(lambda: self.chat.set_up_new_auto_dialog(i))
                    if not self.is_webscraping and i == 0:
                        setup.signals.finished.connect(self.chat.initialize_webscraping)
                    self.gui.threadpool.start(setup)

        if signal == 0:
            # If auto is disabled, close browser windows
            self.is_webscraping = False
            for i in range(0, Data.BUFFER):
                setup = Worker(self.browsers[i].tear_down)
                self.gui.threadpool.start(setup)

    def next_btn(self):
        """
        Loads the next message in the auto_queue into the input box
        """
        # Get value of the currently selected item in the auto_queue
        index = self.auto_history.auto_queue.selectionModel().currentIndex()
        value = index.sibling(index.row(), index.column()).data()
        self.chat_input.setText(value)

        # Jumping to next row in line
        self.auto_history.auto_queue.selectionModel().select(
            index, QItemSelectionModel.Deselect
        )
        index = self.auto_history.auto_queue.model().index(index.row() + 1, 0)
        self.auto_history.auto_queue.setCurrentIndex(index)

        # Jump back to the beginning
        if self.auto_history.auto_queue.selectedIndexes() == []:
            self.auto_history.auto_queue.setCurrentIndex(
                self.auto_history.auto_queue.model().index(0, 0)
            )

    def switch_to_analysis(self):
        self.is_webscraping = False
        self.gui.central_stacked_widget.setCurrentWidget(self.gui.analysis_suite)
        self.gui.populate_search_box()

    def shutdown_browsers(self):
        self.is_webscraping = False
        for browser in self.browsers:
            browser.tear_down()
