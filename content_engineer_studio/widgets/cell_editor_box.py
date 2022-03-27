import typing
import pandas as pd
import numpy as np
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
    QHBoxLayout,
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
from PyQt5 import QtWidgets, QtGui, QtCore

from utils.data_variables import Data, GuiSignals


class CellEditorContainer(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.gui = parent.gui
        self.pgdf = parent.pgdf
        self.suite = parent

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.column_select_layout = QHBoxLayout()
        self.main_layout.addLayout(self.column_select_layout, 0, 0)

        # Cell selector combobox
        self.cell_selector = QtWidgets.QComboBox()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cell_selector.sizePolicy().hasHeightForWidth()
        )
        self.cell_selector.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.cell_selector.setFont(font)
        self.cell_selector.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.cell_selector.setObjectName("cell_selector")
        self.column_select_layout.addWidget(self.cell_selector)

        # Buttons
        self.left = QtWidgets.QPushButton()
        self.left.setMaximumSize(QtCore.QSize(80, 16777215))
        self.left.setObjectName("left")
        self.left.setText("<")
        self.column_select_layout.addWidget(self.left)

        self.right = QtWidgets.QPushButton()
        self.right.setMaximumSize(QtCore.QSize(80, 16777215))
        self.right.setObjectName("right")
        self.right.setText(">")
        self.column_select_layout.addWidget(self.right)

        self.colorize = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorize.sizePolicy().hasHeightForWidth())
        self.colorize.setSizePolicy(sizePolicy)
        self.colorize.setMaximumSize(QtCore.QSize(22, 22))
        self.colorize.setObjectName("colorize")
        self.column_select_layout.addWidget(self.colorize)

        # Cell Editor
        self.cell_editor = CellEdit(parent=self)
        self.cell_editor.setObjectName("cell_editor")
        self.main_layout.addWidget(self.cell_editor, 1, 0)

        # Connecting functions
        self.left.clicked.connect(self.btn_left)
        self.cell_selector.currentIndexChanged.connect(self.populate_analysis)
        self.right.clicked.connect(self.btn_right)
        self.colorize.clicked.connect(self.btn_colorize)

        self.cell_editor.signals.editing_done.connect(self.save_analysis)
        self.gui.signals.columns_reordered.connect(self.check_populate_cell_selector)

    def check_populate_cell_selector(self, name):
        if self.suite.viewer is not None:
            if self.suite.viewer.pgdf.name == name:
                self.populate_cell_selector()

    def populate_cell_selector(self):
        """
        Set model for combobox that displays Data.ROLES['EDITABLE'] rows
        """
        # for _ in range(10):
        #     self.cell_selector.addItem("Banana")
        # return
        self.suite.viewer.pgdf.model[
            "analysis_selector_proxy_model"
        ] = AnalysisSelectorModel(parent=self)

        self.cell_selector.setModel(
            self.suite.viewer.pgdf.model["analysis_selector_proxy_model"]
        )

    def populate_analysis(self):
        if self.cell_selector.model().rowCount() > 0:
            self.cell_editor.setPlainText(
                self.get_string_from_dataframe(
                    self.suite.viewer.pgdf.df_unfiltered.loc[
                        self.suite.row,
                        (self.cell_selector.currentText(), Data.ROLES["EDITABLE"]),
                    ]
                )
            )

    def get_string_from_dataframe(self, value):
        if pd.isna(value):
            return ""

        if isinstance(value, (float, np.floating)):
            return str(round(value, 3))

        return str(value)

    def save_analysis(self):
        """
        Saves current analysis text to dataframe
        """
        self.suite.viewer.pgdf.edit_data(
            row=self.suite.row,
            col=(self.cell_selector.currentText(), Data.ROLES["EDITABLE"]),
            text=self.cell_editor.toPlainText(),
        )

    def btn_left(self):
        if self.cell_selector.currentIndex() > 0:
            self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() - 1)

    def btn_right(self):
        if self.cell_selector.currentIndex() >= self.cell_selector.count() - 1:
            self.cell_selector.setCurrentIndex(0)
            return
        self.cell_selector.setCurrentIndex(self.cell_selector.currentIndex() + 1)

    def btn_colorize(self):
        self.analysis_excel.colorize(
            self.row + 2,
            self.cell_selector.currentIndex() + self.cell_selector_start + 1,
        )


class CellEdit(QTextEdit):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.suite = parent.suite
        self.container = parent

        self.signals = GuiSignals()

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(450, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setAcceptDrops(False)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.setTabChangesFocus(False)
        self.setAcceptRichText(False)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == Qt.Key_Tab:
            self.signals.editing_done.emit()
            self.container.btn_right()
            return
        return super().keyPressEvent(e)

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
        self.signals.editing_done.emit()
        return super().focusOutEvent(e)


class AnalysisSelectorModel(QtCore.QAbstractListModel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.container = parent
        self.df = self.container.suite.viewer.pgdf.df_unfiltered

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        if not isinstance(self.df.columns, pd.MultiIndex):
            return 0
        # print(sum(i == Data.ROLES['EDITABLE'] for i in self.df.columns.get_level_values(1)))
        return sum(
            i == Data.ROLES["EDITABLE"] for i in self.df.columns.get_level_values(1)
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
            rows = tuple(
                x[0] for x in self.df.columns if x[1] == Data.ROLES["EDITABLE"]
            )
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
