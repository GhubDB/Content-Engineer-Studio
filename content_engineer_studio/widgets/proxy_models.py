import typing
import pandas as pd
from PyQt5 import QtCore, QtWidgets


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


class AnalysisSelectorProxyModel(QtCore.QIdentityProxyModel):
    def __init__(self, parent, df) -> None:
        super().__init__(parent)
        self.gui = parent
        self.df = df

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if not isinstance(self.df.columns, pd.MultiIndex):
            return 0
        return sum(
            self.df.columns.get_level_values(1)[i]
            for i in range(0, len(self.df.columns.get_level_values(1)))
        )

    def data(self, index, role):
        if not index.isValid():
            return None

        if not isinstance(self.df.columns, pd.MultiIndex):
            return None

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            # print(row)
            # print(str(self.pgdf.df.columns[row]))
            rows = (x[1] for x in self.df.columns if x[0] == "Editable")
            return str(rows[row])
