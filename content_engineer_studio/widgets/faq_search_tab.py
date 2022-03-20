import typing
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
    QHBoxLayout,
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
    QTableView,
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
from PyQt5 import QtWidgets, QtGui, QtCore


class FaqSearchTabContainer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("faq_search_tab")
        self.main_grid = QtWidgets.QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setObjectName("main_grid")
        self.searchbar = QtWidgets.QLineEdit(self)
        self.searchbar.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchbar.setFont(font)
        self.searchbar.setObjectName("searchbar")
        self.main_grid.addWidget(self.searchbar, 0, 0, 1, 1)
        self.main_gridsearch_column_select = QtWidgets.QComboBox(self.faq)
        self.main_gridsearch_column_select.setMinimumSize(QtCore.QSize(150, 0))
        self.main_gridsearch_column_select.setObjectName(
            "main_gridsearch_column_select"
        )
        self.main_grid.addWidget(self.main_gridsearch_column_select, 0, 1, 1, 1)
        self.close_faq = QtWidgets.QPushButton(self.faq)
        self.close_faq.setMaximumSize(QtCore.QSize(60, 16777215))
        self.close_faq.setObjectName("close_faq")
        self.main_grid.addWidget(self.close_faq, 0, 2, 1, 1)
        self.search_box = QtWidgets.QTableView(self.faq)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_box.sizePolicy().hasHeightForWidth())
        self.search_box.setSizePolicy(sizePolicy)
        self.search_box.setMinimumSize(QtCore.QSize(0, 0))
        self.search_box.setFrameShape(QtWidgets.QFrame.Panel)
        self.search_box.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.search_box.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.search_box.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.search_box.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.search_box.setObjectName("search_box")
        self.search_box.horizontalHeader().setVisible(False)
        self.search_box.horizontalHeader().setStretchLastSection(True)
        self.search_box.verticalHeader().setVisible(False)
        self.main_grid.addWidget(self.search_box, 1, 0, 1, 3)
