import sys
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


class AnalysisSuite(BaseSuite):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        #####################################################
        """Initializing variables"""
        #####################################################

        self.browser = Browser()
        self.viewer = None

        #####################################################
        """Seting up components"""
        #####################################################

        self.setObjectName("analysis_suite")

        # This holds the statusbar and the Go Testing / Export to Testing buttons
        self.toolbar_container = QWidget(self)
        self.toolbar_layout = QtWidgets.QGridLayout(self.toolbar_container)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setObjectName("toolbar_layout")
        self.test = QtWidgets.QPushButton()
        self.test.setMaximumSize(QtCore.QSize(60, 16777215))
        self.test.setObjectName("test")
        self.toolbar_layout.addWidget(self.test, 0, 2, 1, 1)
        self.open_links = QtWidgets.QCheckBox()
        self.open_links.setMaximumSize(QtCore.QSize(90, 16777215))
        self.open_links.setChecked(True)
        self.open_links.setObjectName("open_links")
        self.toolbar_layout.addWidget(self.open_links, 0, 1, 1, 1)
        self.lock_browser = QtWidgets.QPushButton()
        self.lock_browser.setMaximumSize(QtCore.QSize(105, 16777215))
        self.lock_browser.setObjectName("lock_browser")
        self.toolbar_layout.addWidget(self.lock_browser, 0, 3, 1, 1)
        self.switch_to_testing_suite = QtWidgets.QPushButton()
        self.switch_to_testing_suite.setMaximumSize(QtCore.QSize(80, 16777215))
        self.switch_to_testing_suite.setObjectName("switch_to_testing_suite")
        self.toolbar_layout.addWidget(self.switch_to_testing_suite, 0, 5, 1, 1)
        self.status_bar = QtWidgets.QLabel()
        self.status_bar.setMinimumSize(QtCore.QSize(0, 15))
        self.status_bar.setMaximumSize(QtCore.QSize(16777215, 20))
        self.status_bar.setObjectName("status_bar")
        self.toolbar_layout.addWidget(self.status_bar, 0, 0, 1, 1)
        self.export_to_testing_suite = QtWidgets.QPushButton()
        self.export_to_testing_suite.setMaximumSize(QtCore.QSize(120, 16777215))
        self.export_to_testing_suite.setObjectName("export_to_testing_suite")
        self.toolbar_layout.addWidget(self.export_to_testing_suite, 0, 4, 1, 1)
        self.test.setText("Test")
        self.open_links.setText("Open Links")
        self.lock_browser.setText("Lock Browser")
        self.switch_to_testing_suite.setText("Go Testing")
        self.status_bar.setText("Status")
        self.export_to_testing_suite.setText("Export to Testing")
        self.dataframe_chat_grid.addWidget(self.toolbar_container, 1, 0)

        self.export_to_testing_suite.clicked.connect(self.exportToTesting)
        self.switch_to_testing_suite.clicked.connect(self.switchToTesting)

        #####################################################
        """Methods"""
        #####################################################

    def row_selector(self, selected: QtCore.QObject):
        """
        Master Controller. Keeps the current row number updated. Reimplemented from base_suite
        """
        super().row_selector(selected)

        # Loading web page, web scraping and adding results to self.chat
        if self.open_links.checkState():
            # Start a new thread to load the chat log
            setup = Worker(self.chat.getChatlog, "activate_output")
            setup.signals.output.connect(self.chat.populate_chat_analysis)
            self.gui.threadpool.start(setup)

    # def populate_status_bar(self, row: int, start: int, end: int):
    #     self.status_bar.setText(
    #         self.df.iloc[row : row + 1, start : end + 1].to_string(
    #             header=False, index=False
    #         )
    #     )

    def switchToTesting(self):
        self.gui.stackedWidget.setCurrentWidget(self.gui.testing_suite)
        self.gui.populate_search_box()

    def exportToTesting(self):
        customer = self.getChatText(export=True)
        if customer:
            for message in customer:
                # print(message)
                item = QtGui.QStandardItem(message)
                self.gui.testing_suite.auto_history.auto_queue_model.appendRow(item)
        self.gui.stackedWidget.setCurrentWidget(self.gui.testing_suite)
        self.gui.populate_search_box()
