import typing
import re
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
from bs4 import BeautifulSoup

from utils.stylesheets import Stylesheets


class MainChatWidget(QWidget):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        # self.gui = parent.gui

        self.chat = ChatWindow(parent=self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.chat_window)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def getChatText(self, export: typing.Optional[bool] = False) -> str:
        """
        Pulls and anonymizes user selected messages from the chat tablewidget.
        """
        bot = []
        customer = []
        # Iterate over editors in self.chat TableWidget
        for idx in range(0, self.chat.rowCount()):
            editor = self.chat.cellWidget(idx, 0)
            if editor.selected:
                # Convert the text of the message at the grid location to HTML and parse it
                message_html = BeautifulSoup(str(editor), "html.parser")
                # Find all span tags and replace the text with ***
                tags = message_html.find_all("span")
                for tag in tags:
                    tag.string = "***"
                if editor.participant == "bot":
                    bot.append(message_html.get_text().strip())
                else:
                    customer.append(message_html.get_text().strip())
        if export:
            return customer
        return "\n".join(customer), "\n".join(bot)


class ChatWindow(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self = ChatWindow(parent=self)
        self.setMinimumSize(QtCore.QSize(250, 0))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setObjectName("chat")
        self.setColumnCount(0)
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)


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

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:

        # Set Selection
        if e.button() == QtCore.Qt.RightButton:
            self.setSelection()

        # Add variants
        if e.button() == Qt.MiddleButton:
            text = self.toPlainText()
            self.new_variant = AddVariant(text_input=text)

        return super().mousePressEvent(e)


class AddVariant(QWidget):
    """
    Adds FAQ variant questions to the FAQ database
    """

    def __init__(self, parent=None, text_input=None):
        super().__init__(parent)
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


class Highlighter(QSyntaxHighlighter):
    """
    Highlights predefined regular expressions in the chat log
    """

    def __init__(self, document, name, parent=None):
        super().__init__(parent)
        self._mapping = {}
        self.name = name
        self.gui = parent

        # Email addresses
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"  # Working changes
        # pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" # Original
        self.add_mapping(pattern, class_format)

        # Phone numbers
        class_format = QTextCharFormat()
        class_format.setBackground(QColor(68, 126, 237))
        pattern = r"(\b(0041|0)|\B\+41)(\s?\(0\))?([\s\-./,'])?[1-9]{2}([\s\-./,'])?[0-9]{3}([\s\-./,'])?[0-9]{2}([\s\-./,'])?[0-9]{2}\b"
        # class_format.setTextColor(QColor(120, 135, 171))
        self.add_mapping(pattern, class_format)

        self.setDocument(document)

    def add_mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        """
        Reimplemented highlighting function
        """
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.gui.auto_anonymized.append([self.name, start, end])
                # self.setFormat(start, end-start, fmt) # Original implementation
