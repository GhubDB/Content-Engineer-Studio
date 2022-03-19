from PyQt5 import QtWidgets, QtGui, QtCore


class Sidebar(QtWidgets.QTableView):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.gui = parent
        self.setMinimumSize(QtCore.QSize(35, 0))
        self.setMaximumSize(QtCore.QSize(35, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.viewport().setProperty(
            "cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setObjectName("sidebar")
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setDefaultSectionSize(42)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(26)


class SideBarProxyModel(QtCore.QIdentityProxyModel):
    def __init__(self, parent) -> None:
        super().__init__(parent)

    def setSourceModel(self, sourceModel: QtCore.QAbstractItemModel) -> None:
        return super().setSourceModel(sourceModel)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:

        # Remove dotted border on cell focus.  https://stackoverflow.com/a/55252650/3620725
        if option.state & QtWidgets.QStyle.State_HasFocus:
            option.state = option.state ^ QtWidgets.QStyle.State_HasFocus

        options = QtWidgets.QStyleOptionViewItem(option)
        option.widget.style().drawControl(
            QtWidgets.QStyle.CE_ItemViewItem, option, painter, options.widget
        )

        super().paint(painter, option, index)

    # def __init__(self, parent) -> None:
    #     super().__init__(parent)

    # def data(self, proxyIndex: QtCore.QModelIndex, role: int = ...) -> typing.Any:

    # TODO: add a way to insert a different background color for completed rows
    # return super().data(proxyIndex, role)
