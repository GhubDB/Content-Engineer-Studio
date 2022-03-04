from PyQt5 import QtCore, QtGui, QtWidgets
import typing


class DataFrameRowView(QtCore.QSortFilterProxyModel):
    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        return super().data(index, role)
