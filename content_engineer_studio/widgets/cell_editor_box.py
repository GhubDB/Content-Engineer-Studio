import typing
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


class CellEditorContainer(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

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
        self.column_select_layout.addWidget(self.left)

        self.right = QtWidgets.QPushButton()
        self.right.setMaximumSize(QtCore.QSize(80, 16777215))
        self.right.setObjectName("right")
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
        self.cell_editor = QtWidgets.QTextEdit()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cell_editor.sizePolicy().hasHeightForWidth())
        self.cell_editor.setSizePolicy(sizePolicy)
        self.cell_editor.setMinimumSize(QtCore.QSize(450, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cell_editor.setFont(font)
        self.cell_editor.setAcceptDrops(False)
        self.cell_editor.setFrameShape(QtWidgets.QFrame.Panel)
        self.cell_editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.cell_editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.cell_editor.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustIgnored
        )
        self.cell_editor.setTabChangesFocus(False)
        self.cell_editor.setAcceptRichText(False)
        self.cell_editor.setObjectName("cell_editor")
        self.main_layout.addWidget(self.cell_editor, 1, 0)
