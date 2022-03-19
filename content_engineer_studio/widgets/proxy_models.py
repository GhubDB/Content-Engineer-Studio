import typing
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt


from utils.data_variables import multiple_choice


class AnalysisSelectorModel(QtCore.QAbstractListModel):
    def __init__(self, parent, df) -> None:
        super().__init__(parent)
        self.gui = parent
        self.df = df

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if not isinstance(self.df.columns, pd.MultiIndex):
            return 0
        # print(sum(i == "Editable" for i in self.df.columns.get_level_values(1)))
        return sum(i == "Editable" for i in self.df.columns.get_level_values(1))

    def data(self, index, role):
        if not index.isValid():
            return None

        if not isinstance(self.df.columns, pd.MultiIndex):
            return None

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            # print(row)
            # print(str(self.pgdf.df.columns[row]))
            rows = tuple(x[0] for x in self.df.columns if x[1] == "Editable")
            # print(rows)
            # print(self.df.columns)
            return rows[row]

    def flags(self, index):
        """
        https://forum.qt.io/topic/22153/baffled-by-qlistview-drag-drop-for-reordering-list/2
        """
        if index.isValid():
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def beginInsertRows(
        self, parent: QtCore.QModelIndex, first: int, last: int
    ) -> None:
        return super().beginInsertRows(parent, first, last)

    def endInsertRows(self) -> None:
        return super().endInsertRows()

    def setData(
        self, index: QtCore.QModelIndex, value: typing.Any, role: int = Qt.EditRole
    ) -> bool:
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole:
            row = index.row()
            column = index.column()
            rows = tuple(x[0] for x in self.df.columns if x[1] == "Multi-Choice")
            self.pgdf.edit_data(
                row=self.gui.analysis_row
                if self.mode == "analysis"
                else self.gui.testing_row,
                col=(rows[row], "Multi-Choice"),
                text=multiple_choice[column],
            )
            self.dataChanged.emit(index, index)
            # text=np.nan if value == 2 else multiple_choice[column]
            return True

        return False

    def flags(self, index):
        """
        https://forum.qt.io/topic/22153/baffled-by-qlistview-drag-drop-for-reordering-list/2
        """
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def beginInsertRows(
        self, parent: QtCore.QModelIndex, first: int, last: int
    ) -> None:
        return super().beginInsertRows(parent, first, last)

    def endInsertRows(self) -> None:
        return super().endInsertRows()
