import typing
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt


class SideBarProxyModel(QtCore.QIdentityProxyModel):
    def __init__(self, parent) -> None:
        super().__init__(parent)

    def setSourceModel(self, sourceModel: QtCore.QAbstractItemModel) -> None:
        return super().setSourceModel(sourceModel)

    # def __init__(self, parent) -> None:
    #     super().__init__(parent)

    # def data(self, proxyIndex: QtCore.QModelIndex, role: int = ...) -> typing.Any:

    # TODO: add a way to insert a different background color for completed rows
    # return super().data(proxyIndex, role)


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