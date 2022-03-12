import sys
from typing import List, Union
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from pandasgui.widgets.code_history_viewer import CodeHistoryViewer

from pandasgui.widgets.containers import Container
from pandasgui.widgets.dataframe_viewer import DataFrameViewer
from pandasgui.widgets.column_viewer import ColumnViewer
from pandasgui.widgets.grapher import Grapher
from pandasgui.widgets.reshaper import Reshaper
from pandasgui.widgets.filter_viewer import FilterViewer
from pandasgui.widgets.stats_viewer import StatisticsViewer
from pandasgui.widgets.dock_widget import DockWidget
from pandasgui.store import PandasGuiDataFrameStore

import logging

logger = logging.getLogger(__name__)


class DataFrameExplorer(QtWidgets.QWidget):
    def __init__(self, pgdf: PandasGuiDataFrameStore):
        super().__init__()

        pgdf = PandasGuiDataFrameStore.cast(pgdf)
        pgdf.dataframe_explorer = self
        self.pgdf = pgdf

        ##################
        # Set up main views in Dock tabs
        self.main_window = QtWidgets.QMainWindow()
        self.docks: List[DockWidget] = []
        self.main_window.setDockOptions(
            self.main_window.GroupedDragging
            | self.main_window.AllowTabbedDocks
            | self.main_window.AllowNestedDocks
        )
        self.main_window.setTabPosition(
            Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North
        )

        self.dataframe_viewer = DataFrameViewer(pgdf)
        self.statistics_viewer = StatisticsViewer(pgdf)
        self.grapher = Grapher(pgdf)
        self.reshaper = Reshaper(pgdf)
        self.code_history_viewer = CodeHistoryViewer(pgdf)

        self.dataframe_dock = self.add_view(self.dataframe_viewer, "DataFrame")
        self.statistics_dock = self.add_view(self.statistics_viewer, "Statistics")
        self.grapher_dock = self.add_view(self.grapher, "Grapher")
        self.reshaper_dock = self.add_view(self.reshaper, "Reshaper")

        def set_active_tab(name):
            self.active_tab = name

        self.dataframe_dock.activated.connect(lambda: set_active_tab("DataFrame"))
        self.statistics_dock.activated.connect(lambda: set_active_tab("Statistics"))
        self.grapher_dock.activated.connect(lambda: set_active_tab("Grapher"))
        self.reshaper_dock.activated.connect(lambda: set_active_tab("Reshaper"))

        self.dataframe_viewer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        ##################
        # Non-Dock widgets

        self.filter_viewer = FilterViewer(pgdf)
        self.column_viewer = HeaderRolesView(parent=self.dataframe_viewer)
        # self.column_viewer = ColumnArranger(self.pgdf)

        ##################
        # Set up overall layout

        self.splitter = QtWidgets.QSplitter(Qt.Horizontal)
        self.side_bar = QtWidgets.QSplitter(Qt.Vertical)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.splitter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.filter_viewer_container = Container(self.filter_viewer, "Filters")

        self.splitter.addWidget(self.side_bar)
        self.splitter.addWidget(self.main_window)
        self.side_bar.addWidget(self.filter_viewer_container)
        self.side_bar.addWidget(Container(self.column_viewer, "Columns"))
        # self.side_bar.addWidget(Container(self.column_viewer, "Columns"))

    # Add a dock to the MainWindow widget
    def add_view(self, widget: QtWidgets.QWidget, title: str):
        dock = DockWidget(title, self.pgdf.name)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)

        frame = QtWidgets.QFrame()
        frame.setFrameStyle(frame.Box | frame.Raised)
        frame.setLineWidth(2)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(widget)
        frame.setLayout(layout)
        dock.setWidget(frame)

        if len(self.docks) > 0:
            self.main_window.tabifyDockWidget(self.docks[0], dock)
            # Keep the first tab active by default
            self.docks[0].raise_()
        else:
            self.main_window.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.docks.append(dock)
        return dock


class HeaderRolesModel(QtCore.QAbstractListModel):
    def __init__(self, parent):
        super(HeaderRolesModel, self).__init__(parent)
        self.dataframe_viewer: DataFrameViewer = parent
        self.pgdf: PandasGuiDataFrameStore = parent.pgdf

    def rowCount(self, parent):
        return self.pgdf.df_unfiltered.columns.shape[0]

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            row = index.row()
            # print(row)
            # print(str(self.pgdf.df.columns[row]))
            return str(self.pgdf.df_unfiltered.columns[row])

    def setData(self, index, value, role=None):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            # col = index.column()
            try:
                self.pgdf.df.rename(
                    {self.pgdf.df_unfiltered.columns[row]: value},
                    axis="columns",
                    inplace=True,
                )
                self.dataframe_viewer.refresh_ui()
            except Exception as e:
                logger.exception(e)
                return False
            return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return (
            Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsEditable
        )

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(
        self,
        data: "QMimeData",
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QtCore.QModelIndex,
    ) -> bool:

        self.dataframe_viewer._move_column(
            row,
        )
        return super().dropMimeData(data, action, row, column, parent)

    def canDropMimeData(
        self,
        data: "QMimeData",
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QtCore.QModelIndex,
    ) -> bool:
        return super().canDropMimeData(data, action, row, column, parent)

    def beginInsertRows(
        self, parent: QtCore.QModelIndex, first: int, last: int
    ) -> None:
        return super().beginInsertRows(parent, first, last)

    def endInsertRows(self) -> None:
        return super().endInsertRows()


class HeaderRolesView(QtWidgets.QListView):
    def __init__(self, parent: DataFrameViewer = None):
        super().__init__(parent=None)
        if parent is not None:
            self.dataframe_viewer = parent
            self.pgdf: DataFrameViewer = parent.pgdf

            self.orig_model = HeaderRolesModel(parent=self.dataframe_viewer)
            self.setModel(self.orig_model)

        font = QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            print(event.mimeData().formats(), len(event.mimeData().text()))
            event.accept()
        else:
            event.ignore()

    def startDrag(
        self, supportedActions: Union[QtCore.Qt.DropActions, QtCore.Qt.DropAction]
    ) -> None:
        return super().startDrag(supportedActions)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        print(event.pos())
        super().dropEvent(event)
        # self.onDropSignal.emit()


# class ColumnArranger(ColumnViewer):
#     def __init__(self, pgdf: PandasGuiDataFrameStore):
#         super().__init__(pgdf)
#         pgdf = PandasGuiDataFrameStore.cast(pgdf)
#         self.pgdf = pgdf

#         self.tree.setAcceptDrops(True)
#         self.tree.setDragEnabled(True)
#         self.tree.setDefaultDropAction(Qt.MoveAction)
#         self.tree.setHeaderLabels(["Name"])
#         self.refresh()

#         self.setContextMenuPolicy(Qt.CustomContextMenu)

#         self.tree.onDropSignal.connect(self.columns_rearranged)
#         self.tree.itemDoubleClicked.connect(self.on_double_click)

#         self.tree.mouseReleaseEventSignal.connect(self.on_mouseReleaseEvent)

#     def on_double_click(self, item: QtWidgets.QTreeWidgetItem):
#         ix = self.tree.indexOfTopLevelItem(item)
#         self.pgdf.dataframe_viewer.scroll_to_column(ix)

#     def columns_rearranged(self):
#         items = [
#             self.tree.topLevelItem(x).text(0)
#             for x in range(self.tree.topLevelItemCount())
#         ]
#         self.pgdf.reorder_columns(items)

#     def sizeHint(self) -> QtCore.QSize:
#         return QtCore.QSize(200, super().sizeHint().height())

#     def on_mouseReleaseEvent(self, event):
#         # TODO - Add context menu to move columns to front and end
#         return
#         if event.button() == Qt.RightButton:
#             pos = event.pos()
#             item = self.tree.itemAt(pos)
#             ix = self.tree.indexAt(pos)
#             ix_list = [
#                 self.tree.indexOfTopLevelItem(x) for x in self.tree.selectedItems()
#             ]
#             if item:
#                 menu = QtWidgets.QMenu(self.tree)

#                 action1 = QtWidgets.QAction("Move To Front")
#                 action1.triggered.connect(lambda: None)

#                 action2 = QtWidgets.QAction("Move To End")
#                 action2.triggered.connect(lambda: None)

#                 for action in [action1, action2]:
#                     menu.addAction(action)

#                 menu.exec_(QtGui.QCursor().pos())

#         super().mouseReleaseEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    from pandasgui.datasets import pokemon

    # Create and show widget
    dfe = DataFrameExplorer(pokemon)
    dfe.show()

    sys.exit(app.exec_())
