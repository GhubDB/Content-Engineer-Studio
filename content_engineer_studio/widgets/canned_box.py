import typing
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHeaderView
from PyQt5 import QtWidgets, QtGui, QtCore

from utils.data_variables import Data
from PandasGUI.PandasGUI.pandasgui.store import PandasGuiDataFrameStore


class Canned(QtWidgets.QTableView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.gui = parent.gui
        self.suite = parent

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

    def populate_canned(self):
        # Add model to multiple choice selection box
        self.suite.viewer.pgdf.model["canned_model"] = CannedSelectionModel(
            parent=self, pgdf=self.suite.viewer.pgdf
        )
        self.setModel(self.suite.viewer.pgdf.model["canned_model"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().resizeSection(1, 50)
        self.horizontalHeader().resizeSection(2, 70)
        self.horizontalHeader().resizeSection(3, 100)


class CannedSelectionModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, pgdf: PandasGuiDataFrameStore) -> None:
        super().__init__(parent)
        self.gui = parent.gui
        self.suite = parent.suite
        self.container = parent
        self.pgdf = self.container.suite.viewer.pgdf

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(Data.MULTIPLE_CHOICE)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if not isinstance(self.pgdf.df_unfiltered.columns, pd.MultiIndex):
            return 0
        return sum(
            i == Data.ROLES["MULTI_CHOICE"]
            for i in self.pgdf.df_unfiltered.columns.get_level_values(1)
        )

    def data(self, index, role):
        if not index.isValid():
            return None

        if not isinstance(self.pgdf.df_unfiltered.columns, pd.MultiIndex):
            return None

        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            rows = tuple(
                x[0]
                for x in self.pgdf.df_unfiltered.columns
                if x[1] == Data.ROLES["MULTI_CHOICE"]
            )
            if column == 0:
                return rows[row]
            else:
                return Data.MULTIPLE_CHOICE[column]
        elif role == Qt.CheckStateRole and column in [1, 2, 3]:
            # This allows users to select checkboxes
            row = index.row()
            rows = tuple(
                x[0]
                for x in self.pgdf.df_unfiltered.columns
                if x[1] == Data.ROLES["MULTI_CHOICE"]
            )
            # Check if value in Dataframe is equal to the checkbox that is checked
            if (
                self.pgdf.df_unfiltered.loc[
                    self.suite.row, (rows[row], Data.ROLES["MULTI_CHOICE"])
                ]
                == Data.MULTIPLE_CHOICE[column]
            ):
                return Qt.Checked
            else:
                return Qt.Unchecked

    def setData(
        self, index: QtCore.QModelIndex, value: typing.Any, role: int = Qt.EditRole
    ) -> bool:
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            row = index.row()
            column = index.column()
            rows = tuple(
                x
                for x in self.pgdf.df_unfiltered.columns
                if x[1] == Data.ROLES["MULTI_CHOICE"]
            )
            self.pgdf.edit_data(
                row=self.suite.row,
                col=(rows[row]),
                text=Data.MULTIPLE_CHOICE[column],
            )
            self.pgdf.signals.reset_models.emit(["canned_model"])
            return True

        return False

    def flags(self, index):
        """
        https://forum.qt.io/topic/22153/baffled-by-qlistview-drag-drop-for-reordering-list/2
        """
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
