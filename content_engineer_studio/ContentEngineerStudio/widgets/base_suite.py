# Pandasgui imports
from pandasgui.widgets.dataframe_explorer import HeaderRolesViewContainer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (
    QEvent,
    QItemSelectionModel,
    QObject,
    QSortFilterProxyModel,
    Qt,
    QThreadPool,
    QTimer,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QStandardItem,
    QStandardItemModel,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Content Engineer Studio imports
from ContentEngineerStudio.data.data_variables import Data
from ContentEngineerStudio.widgets.canned_box import Canned
from ContentEngineerStudio.widgets.cell_editor_box import CellEditorContainer
from ContentEngineerStudio.widgets.chat_widget import ChatWidgetContainer
from ContentEngineerStudio.widgets.faq_search_box import FaqSearchBoxContainer
from ContentEngineerStudio.widgets.sidebar import Sidebar


class BaseSuite(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.gui = parent
        self.pgdf = None

        self.row = 0

        # Setup UI
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle("Content Engineer Studio")
        self.setContentsMargins(0, 0, 0, 0)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)

        # Set up vertical row selection Sidebar
        self.sidebar = Sidebar(parent=self)
        self.grid.addWidget(self.sidebar, 0, 0, 1, 1)

        self.main_splitter = QtWidgets.QSplitter(self)
        self.main_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.main_splitter.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.main_splitter, 0, 1, 1, 1)

        # This section holds the dataframe viewer and the chat widget
        self.dataframe_chat_container = QWidget(self.main_splitter)
        self.dataframe_chat_grid = QGridLayout(self.dataframe_chat_container)
        self.dataframe_chat_grid.setContentsMargins(0, 0, 0, 0)
        self.dataframe_chat_splitter = QtWidgets.QSplitter(self.main_splitter)
        self.dataframe_chat_splitter.setOrientation(QtCore.Qt.Vertical)
        self.dataframe_chat_grid.addWidget(self.dataframe_chat_splitter, 0, 0)
        self.dataframe_container = QWidget()

        # This Button allows users to add dataframes to the working view
        self.add_dataframe = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.add_dataframe.sizePolicy().hasHeightForWidth()
        )
        self.add_dataframe.setSizePolicy(sizePolicy)
        self.add_dataframe.setText("Add Dataframe")
        self.add_dataframe.setObjectName("add_dataframe")
        self.dataframe_chat_splitter.addWidget(self.add_dataframe)

        # This widget displays chat messages
        self.chat = ChatWidgetContainer(parent=self)
        self.dataframe_chat_splitter.addWidget(self.chat)

        # Holds HeaderRolesViewContainer
        self.roles_view = HeaderRolesViewContainer(parent=None)
        self.main_splitter.addWidget(self.roles_view)

        # Holds FaqSearchBoxContainer, Canned, CellEditor
        self.component_container = QWidget(self.main_splitter)
        self.component_grid = QGridLayout(self.component_container)
        self.component_grid.setContentsMargins(0, 0, 0, 0)
        self.component_splitter = QtWidgets.QSplitter(self.component_container)
        self.component_splitter.setOrientation(QtCore.Qt.Vertical)
        self.component_grid.addWidget(self.component_splitter, 0, 0)

        # FAQ search Box
        self.faq_search_box = FaqSearchBoxContainer(parent=self)
        self.component_splitter.addWidget(self.faq_search_box)

        # This tablewidget displays editable multiple choice selections
        self.canned = Canned(parent=self)
        self.component_splitter.addWidget(self.canned)

        # This container holds the cell editor
        self.cell_editor_box = CellEditorContainer(parent=self)
        self.component_splitter.addWidget(self.cell_editor_box)

        # Up / Save / Down buttons
        self.up_save_down_container = QWidget(self.component_splitter)
        self.up_save_down_layout = QtWidgets.QHBoxLayout(self.up_save_down_container)
        self.up_save_down_layout.setContentsMargins(0, 0, 0, 0)
        self.up = QtWidgets.QPushButton()
        self.up.setObjectName("up")
        self.up.setText("Up")
        self.up_save_down_layout.addWidget(self.up)
        self.save = QtWidgets.QPushButton()
        self.save.setObjectName("save")
        self.save.setText("Save")
        self.up_save_down_layout.addWidget(self.save)
        self.down = QtWidgets.QPushButton()
        self.down.setObjectName("down")
        self.down.setText("Down")
        self.up_save_down_layout.addWidget(self.down)
        self.component_grid.addWidget(self.up_save_down_container, 1, 0)

        # Adjust splitter sizing
        sizes = [99999, 1, 1]
        self.main_splitter.setSizes(sizes)

        """Connecting functions"""
        self.down.clicked.connect(self.btn_down)
        self.up.clicked.connect(self.btn_up)
        self.save.clicked.connect(self.btn_save)
        self.add_dataframe.clicked.connect(
            lambda: self.gui.central_stacked_widget.setCurrentWidget(
                self.gui.pandasgui_container
            )
        )

    def switch_in_dataframe_viewer(self):
        if self.dataframe_chat_splitter.findChild(QPushButton, "add_dataframe"):
            # Replace add_dataframe button with dataframe_viewer
            self.dataframe_chat_splitter.replaceWidget(0, self.viewer)
        else:
            self.dataframe_chat_splitter.insertWidget(0, self.viewer)

    def row_selector(self, selected: QtCore.QObject):
        """
        Master Controller. Keeps the current row number updated
        """
        # Save and clean up before next row is loaded
        self.save_on_row_change()
        self.chat.clear_chat()

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx[0].row() != self.row:
            self.row = idx[0].row()

        if self.viewer.pgdf.model["canned_model"]:
            self.viewer.pgdf.model["canned_model"].beginResetModel()
            self.viewer.pgdf.model["canned_model"].endResetModel()

        self.cell_editor_box.populate_analysis()

        # Autoscrolling to the selection on the sidebar
        self.sidebar.scrollTo(self.sidebar.model().index(self.row, 0))

    def save_on_row_change(self):
        """
        Saves current states to Dataframe
        """
        # Saving analysis
        self.cell_editor_box.cell_editor.signals.editing_done.emit()

        # Getting and saving chat messages
        customer, bot = self.chat.get_chat_text()
        if customer:
            self.save_to_dataframe(role=Data.ROLES["CUSTOMER"], value=customer)
        if bot:
            self.save_to_dataframe(role=Data.ROLES["BOT"], value=bot)

        # Saving correct FAQ
        index = self.faq_search_box.search_box.selectionModel().currentIndex()
        if index.isValid():
            value = index.sibling(index.row(), index.column()).data()
            if value:
                self.save_to_dataframe(role=Data.ROLES["CORRECT_FAQ"], value=value)

        self.viewer.dataView.resizeRowToContents(self.row)
        self.viewer.dataView.resize_header_to_contents(self.row)

    def save_to_dataframe(self, role: str, value: str):
        tuples = tuple(
            x for x in self.viewer.pgdf.df_unfiltered.columns if x[1] == role
        )

        for column in tuples:
            self.viewer.pgdf.edit_data(self.row, column, value)

            self.viewer.pgdf.emit_data_changed(
                column=column,
                row=self.row,
            )

    def btn_up(self):
        self.move_row_up_down(movement=-1)

    def btn_down(self):
        self.move_row_up_down(movement=1)

    def move_row_up_down(self, movement: int):
        if self.viewer is None:
            return
        if self.row < self.viewer.pgdf.df.index.size - 1:
            index = self.sidebar.model().index(self.row + movement, 0)
            self.sidebar.selectionModel().select(
                index,
                QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current,
            )

    def btn_save(self):
        if self.viewer is None:
            return
        self.save_on_row_change()
