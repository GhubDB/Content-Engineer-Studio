import sys
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
from qtstylish import qtstylish

from widgets.base_workarea import BaseWorkarea


class TestingWorkarea(BaseWorkarea):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # self.gui = parent

        # This holds the chat input lineedit and the Send / Next / New Dialog buttons
        self.toolbar_container = QWidget(self)
        self.toolbar_layout = QtWidgets.QHBoxLayout(self.toolbar_container)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setObjectName("toolbar_layout")
        self.auto_2 = QtWidgets.QCheckBox()
        self.auto_2.setMinimumSize(QtCore.QSize(60, 0))
        self.auto_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.auto_2.setObjectName("auto_2")
        self.toolbar_layout.addWidget(self.auto_2)
        self.chat_input = QtWidgets.QLineEdit()
        self.chat_input.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.chat_input.setFont(font)
        self.chat_input.setObjectName("chat_input")
        self.toolbar_layout.addWidget(self.chat_input)
        self.send = QtWidgets.QPushButton()
        self.send.setMaximumSize(QtCore.QSize(70, 16777215))
        self.send.setObjectName("send")
        self.toolbar_layout.addWidget(self.send)
        self.next_question = QtWidgets.QPushButton()
        self.next_question.setMaximumSize(QtCore.QSize(70, 16777215))
        self.next_question.setObjectName("next_question")
        self.toolbar_layout.addWidget(self.next_question)
        self.new_dialog = QtWidgets.QPushButton()
        self.new_dialog.setMinimumSize(QtCore.QSize(90, 0))
        self.new_dialog.setMaximumSize(QtCore.QSize(80, 16777215))
        self.new_dialog.setObjectName("new_dialog")
        self.toolbar_layout.addWidget(self.new_dialog)
        self.auto_2.setText("Auto")
        self.chat_input.setPlaceholderText("Send")
        self.send.setText("Send")
        self.next_question.setText("Next")
        self.new_dialog.setText("New Dialog")
        self.dataframe_chat_grid.addWidget(self.toolbar_container, 1, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    win = AnalysisView()
    win.resize(1920, 180)
    win.show()
    sys.exit(app.exec_())
