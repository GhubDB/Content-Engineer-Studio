import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QGridLayout, QListView, QWidget


class AutoQueue(QListView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setAcceptDrops(True)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setObjectName("auto_queue")


class History(QListView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setObjectName("history")


class AutoqueueAndHistoryContainer(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.gui = parent.gui
        self.suite = parent

        self.main_grid = QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel()
        self.label.setObjectName("auto_queue")
        self.label.setText("Auto Queue")
        self.main_grid.addWidget(self.label, 0, 0, 1, 1)
        self.clear_auto_queue = QtWidgets.QPushButton()
        self.clear_auto_queue.setMaximumSize(QtCore.QSize(80, 16777215))
        self.clear_auto_queue.setObjectName("clear_auto_queue")
        self.clear_auto_queue.setText("Clear")
        self.main_grid.addWidget(self.clear_auto_queue, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setObjectName("history")
        self.label_2.setText("History")
        self.main_grid.addWidget(self.label_2, 0, 2, 1, 1)
        self.clear_history = QtWidgets.QPushButton()
        self.clear_history.setMaximumSize(QtCore.QSize(80, 16777215))
        self.clear_history.setObjectName("clear_history")
        self.clear_history.setText("Clear")
        self.main_grid.addWidget(self.clear_history, 0, 3, 1, 1)

        self.auto_queue = AutoQueue(parent=self)
        self.main_grid.addWidget(self.auto_queue, 1, 0, 1, 2)
        self.history = History(parent=self)
        self.main_grid.addWidget(self.history, 1, 2, 1, 2)

        # Create model for auto_queue and history
        self.auto_queue_model = QStandardItemModel()
        self.auto_queue.setModel(self.auto_queue_model)
        self.auto_queue.installEventFilter(self)

        self.history_model = QStandardItemModel()
        self.history.setModel(self.history_model)

        # Test items
        items = ["Hello there.", "How are you today?", "What are you doing today?"]
        for item in items:
            items = QtGui.QStandardItem(item)
            self.history_model.appendRow(items)

        self.clear_auto_queue.clicked.connect(self.auto_queue_model.clear)
        self.clear_history.clicked.connect(self.history_model.clear)

    def populate_history(self, item_to_add):
        item = QtGui.QStandardItem(item_to_add)
        # if self.dialog_num % 2 == 0:
        #     item.setBackground(QColor(70, 81, 70))
        # else:
        #     item.setBackground(QColor(74, 69, 78))
        self.history_model.appendRow(item)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent):
        # Delete items from Auto Queue
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                indices = self.auto_queue.selectionModel().selectedRows()
                for index in sorted(indices):
                    self.auto_queue_model.removeRow(index.row())
        return super().eventFilter(source, event)
