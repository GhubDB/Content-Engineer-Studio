import sys
from typing import List, Optional, Union
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
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
        self.roles_view = HeaderRolesViewContainer(parent=self)

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
        self.side_bar.addWidget(self.roles_view)

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


class HeaderRolesViewContainer(QtWidgets.QWidget):
    def __init__(self, parent: Optional[DataFrameExplorer] = None):
        super().__init__(parent)
        if parent is not None:
            self.dataframe_explorer = parent
            self.pgdf: DataFrameViewer = parent.pgdf
            self.gui = self.dataframe_explorer.pgdf.store.gui

        # Set up elements
        self.main_layout = QtWidgets.QVBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.add_column_count = QtWidgets.QSpinBox()
        self.add_column_count.setMaximumSize(QtCore.QSize(35, 16777215))
        self.add_column_count.setMinimum(1)
        self.add_column = QtWidgets.QPushButton()
        self.add_column.setText("Add Column(s)")
        self.delete_column = QtWidgets.QPushButton()
        self.delete_column.setText("Delete Column")

        self.button_layout.addWidget(self.add_column_count)
        self.button_layout.addWidget(self.add_column)
        self.button_layout.addWidget(self.delete_column)

        self.search_columns = QtWidgets.QLineEdit()
        self.search_columns.setPlaceholderText("Search columns")
        self.main_layout.addWidget(self.search_columns)

        self.column_viewer = HeaderRolesView(
            parent=self.dataframe_explorer if parent is not None else None
        )
        self.main_layout.addWidget(self.column_viewer)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Connecting buttons and filters
        self.add_column.clicked.connect(self.btn_add_column)
        self.delete_column.clicked.connect(self.btn_delete_column)

        # Initializing models
        if parent is not None:
            self.pgdf.model["header_roles_model"] = HeaderRolesModel(
                parent=self.dataframe_explorer
            )

            self.pgdf.model["column_search_model"] = QtCore.QSortFilterProxyModel()
            self.pgdf.model["column_search_model"].setSourceModel(
                self.pgdf.model["header_roles_model"]
            )
            self.pgdf.model["column_search_model"].setFilterCaseSensitivity(
                Qt.CaseInsensitive
            )
            self.pgdf.model["column_search_model"].setFilterKeyColumn(-1)
            self.search_columns.textChanged.connect(
                self.pgdf.model["column_search_model"].setFilterRegExp
            )
            self.column_viewer.setModel(self.pgdf.model["column_search_model"])
            self.installEventFilter(self)

    def replace_model(self, pgdf, parent, dataframe_explorer):
        self.pgdf = pgdf
        self.column_viewer.setModel(self.pgdf.model["column_search_model"])
        self.search_columns.textChanged.connect(
            self.pgdf.model["column_search_model"].setFilterRegExp
        )
        self.gui = parent
        self.dataframe_explorer = dataframe_explorer

    @pyqtSlot(QtCore.QItemSelection)
    def get_source_from_selection(self):
        """
        Map Proxy model selection to source model selection and return list of selected rows
        https://stackoverflow.com/questions/61268687/access-original-index-in-qabstracttablemodel-from-selected-row-in-qtableview
        """
        index = self.gui.stackedWidget.currentIndex()
        if index == 0:
            hasSelection = (
                self.gui.analysis_suite.roles_view.column_viewer.selectionModel().hasSelection()
            )
            if hasSelection:
                selectedRows = (
                    self.gui.analysis_suite.roles_view.column_viewer.selectionModel().selectedRows()
                )
        if index == 1:
            hasSelection = (
                self.gui.testing_suite.roles_view.column_viewer.selectionModel().hasSelection()
            )
            if hasSelection:
                selectedRows = (
                    self.gui.testing_suite.roles_view.column_viewer.selectionModel().selectedRows()
                )
        if index == 3:
            hasSelection = self.column_viewer.selectionModel().hasSelection()
            if hasSelection:
                selectedRows = self.column_viewer.selectionModel().selectedRows()
        if hasSelection:
            return sorted(
                [
                    self.pgdf.model["column_search_model"].mapToSource(row).row()
                    for row in selectedRows
                ]
            )

    def btn_add_column(self):
        n = self.add_column_count.value()
        rows = self.get_source_from_selection()
        if not rows:
            # TODO: add tooltip saying that a column needs to be selected
            return
        self.dataframe_explorer.pgdf.add_column(
            first=rows[-1] + 1, last=rows[-1] + n + 1
        )

    def btn_delete_column(self):
        rows = self.get_source_from_selection()
        if not rows:
            return
        self.dataframe_explorer.pgdf.delete_column(rows)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        # Enable deleting selected rows with DEL
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.btn_delete_column()
        return super().eventFilter(source, event)


class HeaderRolesModel(QtCore.QAbstractListModel):
    def __init__(self, parent):
        super(HeaderRolesModel, self).__init__(parent)
        self.dataframe_explorer: DataFrameExplorer = parent
        self.pgdf: PandasGuiDataFrameStore = parent.pgdf

    def rowCount(self, parent):
        return self.pgdf.df_unfiltered.columns.shape[0]

    # def columnCount(self, parent: QtCore.QModelIndex) -> int:
    #     print(self.pgdf.df_unfiltered.columns.nlevels)
    #     return self.pgdf.df_unfiltered.columns.nlevels

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            row = index.row()
            # print(row)
            # print(str(self.pgdf.df.columns[row]))
            return str(self.pgdf.df_unfiltered.columns.get_level_values(0)[row])

    def setData(self, index, value, role=None):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            # col = index.column()
            try:
                # self.pgdf.df_unfiltered.columns.values[row] = value
                self.pgdf.df_unfiltered.rename(
                    {self.pgdf.df_unfiltered.columns.get_level_values(0)[row]: value},
                    level=0,
                    axis="columns",
                    inplace=True,
                )
                self.dataframe_explorer.pgdf.refresh_ui()
            except Exception as e:
                logger.exception(e)
                return False
            return True
        return False

    def flags(self, index):
        """
        https://forum.qt.io/topic/22153/baffled-by-qlistview-drag-drop-for-reordering-list/2
        """
        if index.isValid():
            return (
                Qt.ItemIsSelectable
                | Qt.ItemIsDragEnabled
                | Qt.ItemIsEnabled
                | Qt.ItemIsEditable
            )

        return (
            Qt.ItemIsSelectable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsEnabled
            | Qt.ItemIsEditable
        )

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(
        self,
        data: QtCore.QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QtCore.QModelIndex,
    ) -> bool:
        selected = sorted(
            self.dataframe_explorer.roles_view.get_source_from_selection()
        )
        if not selected:
            return False
        if row == -1:
            return False
        # print(selected, row)
        self.pgdf.reorder_columns(selected, row)
        return super().dropMimeData(data, action, row, column, parent)

    # def canDropMimeData(
    #     self,
    #     data: "QMimeData",
    #     action: Qt.DropAction,
    #     row: int,
    #     column: int,
    #     parent: QtCore.QModelIndex,
    # ) -> bool:
    #     return super().canDropMimeData(data, action, row, column, parent)

    def beginInsertRows(
        self, parent: QtCore.QModelIndex, first: int, last: int
    ) -> None:
        return super().beginInsertRows(parent, first, last)

    def endInsertRows(self) -> None:
        return super().endInsertRows()


class HeaderRolesView(QtWidgets.QListView):
    def __init__(self, parent: DataFrameExplorer):
        super().__init__(parent)
        if parent is not None:
            self.dataframe_explorer = parent
            self.pgdf: DataFrameViewer = parent.pgdf

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

        self.setMovement(QtWidgets.QListView.Snap)
        self.setDragDropOverwriteMode(False)
        # self.header().hide()
        # self.setRootIsDecorated(False)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
        return super().dragMoveEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        event.setDropAction(Qt.MoveAction)
        super().dropEvent(event)

    # def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
    #     if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
    #         event.accept()
    #     else:
    #         event.ignore()

    # def startDrag(
    #     self, supportedActions: Union[QtCore.Qt.DropActions, QtCore.Qt.DropAction]
    # ) -> None:
    #     return super().startDrag(supportedActions)

    #     # self.onDropSignal.emit()

    # def dropIndicatorPosition(self) -> "QAbstractItemView.DropIndicatorPosition":
    #     return super().dropIndicatorPosition()

    # def showDropIndicator(self) -> bool:
    #     return super().showDropIndicator()

    # def setDropIndicatorShown(self, enable: bool) -> None:
    #     return super().setDropIndicatorShown(enable)


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
