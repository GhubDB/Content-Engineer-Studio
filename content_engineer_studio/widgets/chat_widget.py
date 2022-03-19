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
    QTextEdit,
    QLabel,
    QPushButton,
    QWidget,
    QGridLayout,
    QMainWindow,
    QHeaderView,
    QTableWidgetItem,
    QTableWidget,
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
from PyQt5 import QtCore, QtWidgets, QtGui

from utils.stylesheets import Stylesheets


class MainChatWidget(QWidget):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        # self.gui = parent.gui

        self.chat_window = QTableWidget(self)
        self.chat_window.setMinimumSize(QtCore.QSize(250, 0))
        self.chat_window.setFrameShape(QtWidgets.QFrame.Panel)
        self.chat_window.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chat_window.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chat_window.setObjectName("chat")
        self.chat_window.setColumnCount(0)
        self.chat_window.setRowCount(0)
        self.chat_window.horizontalHeader().setVisible(False)
        self.chat_window.verticalHeader().setVisible(False)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.chat_window)
        self.main_layout.setContentsMargins(0, 0, 0, 0)


class TextEdit(QTextEdit):
    """
    Custom implementation for auto resizing text edits in tables
    and keeping track of user selected messages
    """

    def __init__(
        self,
        *args,
        participant,
        index,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.updateGeometry)
        self.participant = participant
        self.index = index
        self.selected = False

    # Handles setting style change when user selects a message
    # as well as setting the selection status.
    def setSelection(self):
        if self.selected:
            self.selected = False
            if self.participant == "bot":
                self.setStyleSheet(Stylesheets.bot)
            else:
                self.setStyleSheet(Stylesheets.customer)
        else:
            self.selected = True
            if self.participant == "bot":
                self.setStyleSheet(Stylesheets.bot_selected)
            else:
                self.setStyleSheet(Stylesheets.customer_selected)

    def __str__(self):
        return self.toHtml()

    def sizeHint(self):
        # Auto resizing text editors
        hint = super().sizeHint()
        if self.toPlainText():
            doc = self.document().clone()
            width = self.width() - self.frameWidth() * 2
            if self.verticalScrollBar().isVisible():
                width -= self.verticalScrollBar().width()
            doc.setTextWidth(width)
            height = round(doc.size().height())
        else:
            height = self.fontMetrics().height()
            height += self.document().documentMargin() * 2
        height += self.frameWidth() * 2
        hint.setHeight(height)
        return hint


class AddVariant(QWidget):
    """
    Adds FAQ variant questions to the FAQ database
    """

    def __init__(self, parent=None, text_input=None):
        super(AddVariant, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("Add Variant")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.variant = QTextEdit(objectName="variant_text")
        self.variant.setText(text_input)
        self.variant.setStyleSheet(
            "font-size: 11pt; \
                    border-style: outset; \
                    border-left-width: 5px; \
                    border-left-color: rgb(83, 43, 114); \
                    padding-left: 4px; \
                    background-color: rgb(90, 90, 90);"
        )
        self.variant.installEventFilter(self)
        self.variant.setMinimumWidth(700)

        add_variant = QPushButton(text="Add Variant", objectName="add_variant")
        self.cancel_variant = QPushButton(
            text="Cancel", objectName="cancel_add_variant"
        )
        self.cancel_variant.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.layout.addWidget(self.variant, 0, 0, 1, 2)
        self.layout.addWidget(add_variant, 1, 0, 1, 1)
        self.layout.addWidget(self.cancel_variant, 1, 1, 1, 1)
        self.setLayout(self.layout)
        self.show()
