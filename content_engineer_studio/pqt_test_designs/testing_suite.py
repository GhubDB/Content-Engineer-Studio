import sys, re, time, traceback
from threading import Thread
from warnings import filters
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *
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
from utils.excel_helpers import Excel
from utils.selenium_helpers import Browser
from utils.data_variables import *
from utils.stylesheets import Stylesheets
from bs4 import BeautifulSoup
import qtstylish

# PandasGUI imports
import inspect
import os
import pprint
from typing import Callable, Union, List, Optional
from dataclasses import dataclass
import pandas as pd
import pkg_resources
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import pandasgui
from pandasgui.store import PandasGuiStore
from pandasgui.utility import as_dict, fix_ipython, get_figure_type, resize_widget
from pandasgui.widgets.find_toolbar import FindToolbar
from pandasgui.widgets.json_viewer import JsonViewer
from pandasgui.widgets.navigator import Navigator
from pandasgui.widgets.figure_viewer import FigureViewer
from pandasgui.widgets.settings_editor import SettingsEditor
from pandasgui.widgets.python_highlighter import PythonHighlighter
from IPython.core.magic import register_line_magic
import logging


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Get a grip of table view row height MRE")
        self.setGeometry(QtCore.QRect(100, 100, 1000, 800))
        layout = QtWidgets.QVBoxLayout()
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.table_view = SegmentsTableView(self)
        self.setCentralWidget(central_widget)
        layout.addWidget(self.table_view)
        rows = [
            [
                "one potatoe two potatoe\none potatoe two potatoe \n\none potatoe two potatoe ",
                "one potatoe two potatoe",
            ],
            [
                "Sed ut perspiciatis, unde omnis iste natus error sit voluptatem accusantium doloremque",
                "Sed ut <b>perspiciatis, unde omnis <i>iste natus</b> error sit voluptatem</i> accusantium doloremque",
            ],
            [
                "Nemo enim ipsam voluptatem, quia voluptas sit, aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qui ratione voluptatem sequi nesciunt, neque porro quisquam est, qui do lorem ipsum, quia dolor sit amet consectetur adipiscing velit, sed quia non numquam do eius modi tempora incididunt, ut labore et dolore magnam aliquam quaerat voluptatem.",
                "Nemo enim ipsam <i>voluptatem, quia voluptas sit, <b>aspernatur aut odit aut fugit, <u>sed quia</i> consequuntur</u> magni dolores eos</b>, qui ratione voluptatem sequi nesciunt, neque porro quisquam est, qui do lorem ipsum, quia dolor sit amet consectetur adipiscing velit, sed quia non numquam do eius modi tempora incididunt, ut labore et dolore magnam aliquam quaerat voluptatem.",
            ],
            ["Ut enim ad minima veniam", "Ut enim ad minima veniam"],
            [
                "Quis autem vel eum iure reprehenderit",
                "Quis autem vel eum iure reprehenderit",
            ],
            [
                "At vero eos et accusamus et iusto odio dignissimos ducimus, qui blanditiis praesentium voluptatum deleniti atque corrupti, quos dolores et quas molestias excepturi sint, obcaecati cupiditate non provident, similique sunt in culpa, qui officia deserunt mollitia animi, id est laborum et dolorum fuga.",
                "At vero eos et accusamus et iusto odio dignissimos ducimus, qui blanditiis praesentium voluptatum deleniti atque corrupti, quos dolores et quas molestias excepturi sint, obcaecati cupiditate non provident, similique sunt in culpa, qui officia deserunt mollitia animi, id est laborum et dolorum fuga.",
            ],
        ]
        for n_row, row in enumerate(rows):
            self.table_view.model().insertRow(n_row)
            self.table_view.model().setItem(n_row, 0, QtGui.QStandardItem(row[0]))
            self.table_view.model().setItem(n_row, 1, QtGui.QStandardItem(row[1]))
        self.table_view.setColumnWidth(0, 400)
        self.table_view.setColumnWidth(1, 400)
        self.qle = QtWidgets.QLineEdit()
        layout.addWidget(self.qle)


class DelegateRichTextEditor(QtWidgets.QTextEdit):
    commit = QtCore.pyqtSignal(QtWidgets.QWidget)
    sizeHintChanged = QtCore.pyqtSignal()
    storedSize = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(0)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.contentTimer = QtCore.QTimer(self, timeout=self.contentsChange, interval=0)
        self.document().setDocumentMargin(0)
        self.document().contentsChange.connect(self.contentTimer.start)

    @QtCore.pyqtProperty(str, user=True)
    def content(self):
        text = self.toHtml()
        # find the end of the <body> tag and remove the new line character
        bodyTag = text.find(">", text.find("<body")) + 1
        if text[bodyTag] == "\n":
            text = text[:bodyTag] + text[bodyTag + 1 :]
        return text

    @content.setter
    def content(self, text):
        self.setHtml(text)

    def contentsChange(self):
        newSize = self.document().size()
        if self.storedSize != newSize:
            self.storedSize = newSize
            self.sizeHintChanged.emit()

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.key() in (QtCore.Qt.Key_Return,):
                self.commit.emit(self)
                return
            elif event.key() == QtCore.Qt.Key_B:
                if self.fontWeight() == QtGui.QFont.Bold:
                    self.setFontWeight(QtGui.QFont.Normal)
                else:
                    self.setFontWeight(QtGui.QFont.Bold)
            elif event.key() == QtCore.Qt.Key_I:
                self.setFontItalic(not self.fontItalic())
            elif event.key() == QtCore.Qt.Key_U:
                self.setFontUnderline(not self.fontUnderline())
        super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)


class SegmentsTableViewDelegate(QtWidgets.QStyledItemDelegate):
    rowSizeHintChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editors = {}

    def createEditor(self, parent, option, index):
        pIndex = QtCore.QPersistentModelIndex(index)
        editor = self.editors.get(pIndex)
        if not editor:
            editor = DelegateRichTextEditor(parent)
            editor.sizeHintChanged.connect(
                lambda: self.rowSizeHintChanged.emit(pIndex.row())
            )
            self.editors[pIndex] = editor
        return editor

    def eventFilter(self, editor, event):
        if (
            event.type() == event.KeyPress
            and event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return)
        ):
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
            return True
        return super().eventFilter(editor, event)

    def destroyEditor(self, editor, index):
        # remove the editor from the dict so that it gets properly destroyed;
        # this avoids any "wrapped C++ object destroyed" exception
        self.editors.pop(QtCore.QPersistentModelIndex(index))
        super().destroyEditor(editor, index)
        # emit the signal again: if the data has been rejected, we need to
        # restore the correct hint
        self.rowSizeHintChanged.emit(index.row())

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        painter.save()
        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(0)
        doc.setTextWidth(option.rect.width())
        doc.setHtml(option.text)
        option.text = ""
        option.widget.style().drawControl(
            QtWidgets.QStyle.CE_ItemViewItem, option, painter
        )
        painter.translate(option.rect.left(), option.rect.top())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        self.initStyleOption(option, index)
        editor = self.editors.get(QtCore.QPersistentModelIndex(index))
        if editor:
            doc = QtGui.QTextDocument.clone(editor.document())
        else:
            doc = QtGui.QTextDocument()
            doc.setDocumentMargin(0)
            doc.setHtml(option.text)
            doc.setTextWidth(option.rect.width())
        doc_height_int = int(doc.size().height())
        return QtCore.QSize(int(doc.idealWidth()), doc_height_int)


# class SegmentsTableView(QtWidgets.QTableView):
#     def __init__(self, parent):
#         super().__init__(parent)


class SegmentsTableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        delegate = SegmentsTableViewDelegate(self)
        self.setItemDelegate(delegate)
        delegate.rowSizeHintChanged.connect(self.resizeRowToContents)
        self.setModel(QtGui.QStandardItemModel())

    def showEvent(self, event):
        self.resizeRowsToContents()
        event.accept()


app = QtWidgets.QApplication([])
# app.setFont(default_font)
main_window = MainWindow()
main_window.show()
exec_return = app.exec()
sys.exit(exec_return)
