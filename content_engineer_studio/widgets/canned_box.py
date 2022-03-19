import typing
import pandas as pd
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

from utils.data_variables import multiple_choice
from PandasGUI.PandasGUI.pandasgui.store import PandasGuiDataFrameStore


class Canned(QtWidgets.QTableView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setMinimumSize(QtCore.QSize(0, 120))
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QtCore.QSize(16777215, 200))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setShowGrid(False)
        self.setGridStyle(QtCore.Qt.SolidLine)
        self.setObjectName("canned")
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)


class CannedSelectionModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, pgdf: PandasGuiDataFrameStore, mode) -> None:
        super().__init__(parent)
        self.gui = parent
        self.pgdf = pgdf
        self.df = pgdf.df_unfiltered
        self.mode = mode

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(multiple_choice)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if not isinstance(self.df.columns, pd.MultiIndex):
            return 0
        return sum(i == "Multi-Choice" for i in self.df.columns.get_level_values(1))

    def data(self, index, role):
        if not index.isValid():
            return None

        if not isinstance(self.df.columns, pd.MultiIndex):
            return None

        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            rows = tuple(x[0] for x in self.df.columns if x[1] == "Multi-Choice")
            row = index.row()
            if column == 0:
                return rows[row]
            else:
                return multiple_choice[column]
        elif role == Qt.CheckStateRole and column in [1, 2, 3]:
            rows = tuple(x[0] for x in self.df.columns if x[1] == "Multi-Choice")
            row = index.row()
            if (
                self.df.loc[self.gui.analysis_row, (rows[row], "Multi-Choice")]
                == multiple_choice[column]
            ):
                return Qt.Checked
            else:
                return Qt.Unchecked
