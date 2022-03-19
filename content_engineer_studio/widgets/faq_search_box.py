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
from utils.model_test import ModelTest


class FaqSearchBoxContainer(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Search Text input
        self.searchbar_layout = QHBoxLayout()
        self.searchbar_layout.setContentsMargins(0, 0, 0, 0)
        self.searchbar = QtWidgets.QLineEdit()
        self.searchbar.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchbar.setFont(font)
        self.searchbar.setObjectName("searchbar")
        self.searchbar_layout.addWidget(self.searchbar)
        self.main_layout.addLayout(self.searchbar_layout, 0, 0)

        # Column select Combobox
        self.search_column_select = QtWidgets.QComboBox()
        self.search_column_select.setObjectName("search_column_select")
        self.searchbar_layout.addWidget(self.search_column_select)

        # FAQ display Tableview
        self.search_box = QtWidgets.QTableView()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
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
        self.search_box.setObjectName("search_box")
        self.search_box.horizontalHeader().setVisible(False)
        self.search_box.horizontalHeader().setStretchLastSection(True)
        self.search_box.verticalHeader().setVisible(False)

        self.main_layout.addWidget(self.search_box, 1, 0)
