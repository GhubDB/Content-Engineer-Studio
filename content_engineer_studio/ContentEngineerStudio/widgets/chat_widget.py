import re
import time
import typing

from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import (
    QGridLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ContentEngineerStudio.data.data_variables import Data
from ContentEngineerStudio.utils.highlighter import Highlighter
from ContentEngineerStudio.utils.stylesheets import Stylesheets
from ContentEngineerStudio.utils.worker_thread import Worker


class ChatWidgetContainer(QWidget):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        if parent:
            self.gui = parent.gui
            self.suite = parent
        self.highlighters = {}
        self.auto_anonymized = []
        self.dialog_num = 0
        self.current_browser = 0

        self.is_webscraping = False

        # Chat Widget
        self.chat = ChatWindow(parent=self if hasattr(self, "gui") else None)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.chat)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def get_chat_log(self, output):
        """
        Accesses URL and downloads chat log - used in Analysis
        """
        tuples = tuple(
            x
            for x in self.suite.viewer.pgdf.df_unfiltered.columns
            if x[1] == Data.ROLES["LINK"]
        )

        if len(tuples) < 1:
            return

        if not self.suite.browser.get_url(
            url=self.suite.viewer.pgdf.df_unfiltered.loc[self.suite.row, tuples[0]]
        ):
            self.suite.browser.setUp(
                url=self.suite.viewer.pgdf.df_unfiltered.loc[self.suite.row, tuples[0]]
            )
        chat_text = self.suite.browser.get_cleverbot_static()
        output.emit(chat_text)

    def populate_chat_analysis(self, chat: list[list[str]]):
        """
        Displays webscraped chat messages in chat TableWidget
        """
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(chat))
        for (idx, sender) in enumerate(chat):
            combo = TextEdit(
                self, objectName=f"{sender[0]}_{idx}", participant=sender[0], index=idx
            )
            self.chat.setCellWidget(idx, 0, combo)

            # Add auto highlighting
            if sender[0] == "customer":
                self.highlighters[idx] = Highlighter(
                    document=combo.document(), name=combo, parent=self
                )

            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)

            if sender[0] == "bot":
                combo.setStyleSheet(Stylesheets.bot)
            else:
                combo.setStyleSheet(Stylesheets.customer)

            combo.textChanged.connect(
                lambda idx=idx: self.chat.resizeRowToContents(idx)
            )
            combo.cursorPositionChanged.connect(self.highlight_selection)
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anynomyzify()

    def populate_chat_testing(self, chat: list[list[str]]):
        output = []
        # Add new messages that are not empty strings to output and reset table
        [
            output.append(message)
            for message in chat
            if message not in self.suite.sent_messages and "" not in message
        ]
        self.chat.setColumnCount(1)
        length = len(self.suite.sent_messages)
        self.chat.setRowCount(length + len(output))
        for (
            idx,
            sender,
        ) in enumerate(output, start=length):
            if sender[0] == "bot":
                combo = TextEdit(
                    self, objectName=f"bot_{idx}", participant="bot", index=idx
                )
            else:
                combo = TextEdit(
                    self,
                    objectName=f"customer_{idx}",
                    participant="customer",
                    index=idx,
                )
            self.chat.setCellWidget(idx, 0, combo)
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            # Bot
            if sender[0] == "bot":
                combo.setStyleSheet(Stylesheets.bot)
            # customer
            else:
                combo.setStyleSheet(Stylesheets.customer)
            # Add auto resizing of editor and highlighting
            combo.textChanged.connect(
                lambda idx=idx: self.chat.resizeRowToContents(idx)
            )
            combo.cursorPositionChanged.connect(self.highlight_selection)
        [self.suite.sent_messages.append(message) for message in output]
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def set_up_new_dialog(self):
        """
        Sets up (singular) new chat session
        """
        self.suite.browsers[self.current_browser].setUp(url=Data.LIVECHAT_URL)
        self.suite.browsers[self.current_browser].click_cleverbot_agree()

        self.clear_chat()
        return

    def set_up_new_auto_dialog(self, i: int) -> None:
        """
        Prebuffers browser windows and asks auto_queue questions
        """
        if self.suite.browsers[i].setUp(url=Data.LIVECHAT_URL):
            self.suite.browsers[i].click_cleverbot_agree()
            self.suite.browsers[i].prebuffer_auto_tab(self.suite.questions)
        return

    def initialize_webscraping(self):
        """
        Start new webscraping thread
        """
        # Check if there is a running webscraping thread
        if not self.is_webscraping:
            self.is_webscraping = True
            # Pass the function to execute
            live_webscraper = Worker(self.chat_webscraping_loop, "activate_output")
            # Catch signal of new chat messages
            live_webscraper.signals.output.connect(self.populate_chat_testing)
            # Execute
            self.gui.threadpool.start(live_webscraper)

    def chat_webscraping_loop(self, output: QtCore.pyqtSignal):
        """
        Continuously fetches new messages from the chat page
        """
        while self.is_webscraping:
            try:
                chats = self.suite.browsers[self.current_browser].get_cleverbot_live()
                if chats:
                    output.emit(chats)
                time.sleep(5)
            except:
                time.sleep(5)
                continue

    def highlight_selection(self):
        """
        Highlights and unhighlights user selected text
        """
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        fmt = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4282679021:
            fmt.setBackground(QColor(68, 126, 237))
        else:
            fmt.clearBackground()
        cursor.setCharFormat(fmt)

    def anynomyzify(self):
        """
        Receives starting and ending positions
        of words to select from the Highlighter subclass and selects them
        """
        for name, start, end in self.auto_anonymized:
            cursor = name.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            name.setTextCursor(cursor)
            # cursor.clearSelection()
        self.auto_anonymized = []

    def get_chat_text(self, export: typing.Optional[bool] = False) -> str:
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
        return (
            "\n".join(customer) if customer else False,
            "\n".join(bot) if bot else False,
        )

    def clear_chat(self):
        self.dialog_num += 1
        self.chat.clear()
        self.chat.setRowCount(0)
        self.suite.sent_messages = []


class ChatWindow(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        if parent:
            self.gui = parent.gui

        self.setMinimumSize(QtCore.QSize(250, 0))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setObjectName("chat")
        self.setColumnCount(0)
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        self.installEventFilter(self)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent):
        # Resizing chat message textedits
        if event.type() == event.Resize:
            QTimer.singleShot(0, self.resizeRowsToContents)
        return super().eventFilter(source, event)


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
        self.new_variant = None

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
