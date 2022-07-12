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
    QListView,
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


class Flows(QListView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(16000000, 16777215))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setObjectName("flows")
        self.setColumnCount(0)
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

    def populate_flows(self, flows):
        self.flows.setColumnCount(1)
        self.flows.setRowCount(len(flows))
        for idx, row in enumerate(flows):
            self.flows.setItem(idx, 0, QTableWidgetItem(row))
        self.flows.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


class Actions(QListView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(16000000, 16777215))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.setShowGrid(False)
        self.setObjectName("actions")
        self.setColumnCount(0)
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setHighlightSections(False)

    def populate_actions(self, actions):
        self.actions.setColumnCount(1)
        self.actions.setRowCount(len(actions))
        for idx, row in enumerate(actions):
            self.actions.setItem(idx, 0, QTableWidgetItem(row))
        self.actions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.actions.resizeColumnsToContents()
