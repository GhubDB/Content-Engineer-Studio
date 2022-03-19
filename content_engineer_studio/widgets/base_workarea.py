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

from PyQt5 import QtCore, QtGui, QtWidgets

# Pandasgui imports
from pandasgui.widgets.dataframe_explorer import HeaderRolesViewContainer
from widgets.canned_box import Canned
from widgets.cell_editor_box import CellEditorContainer
from widgets.faq_search_box import FaqSearchBoxContainer

# Content Engineer Studio imports
from widgets.sidebar import Sidebar
from widgets.chat_widget import MainChatWidget


class BaseWorkarea(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.gui = parent

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)

        # Vertical row selection Sidebar
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
        self.dataframe_layout = QtWidgets.QHBoxLayout(self.dataframe_container)
        self.dataframe_layout.setContentsMargins(0, 0, 0, 0)

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
        self.dataframe_layout.addWidget(self.add_dataframe)

        # This widget displays chat messages
        self.chat = MainChatWidget(parent=self)
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
        self.faq_search_box = FaqSearchBoxContainer()
        self.component_splitter.addWidget(self.faq_search_box)

        # This tablewidget displays editable multiple choice selections
        self.canned = Canned()
        self.component_splitter.addWidget(self.canned)

        # This container holds the cell editor
        self.cell_editor = CellEditorContainer()
        self.component_splitter.addWidget(self.cell_editor)

        # Up / Save / Down
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

        sizes = [99999, 1, 1]
        self.main_splitter.setSizes(sizes)
