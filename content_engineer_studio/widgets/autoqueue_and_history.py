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

class AutoqueueAndHistoryContainer(QWidget):


        # Create model for auto_queue and history
        self.auto_queue_model = QStandardItemModel()
        self.auto_queue.setModel(self.auto_queue_model)
        self.auto_queue.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.auto_queue.installEventFilter(self)

        self.history_model = QStandardItemModel()
        self.history.setModel(self.history_model)
        self.history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Test items
        items = ["Hello there.", "How are you today?", "What are you doing today?"]
        for item in items:
            items = QtGui.QStandardItem(item)
            self.history_model.appendRow(items)

        self.clear.clicked.connect(lambda: self.auto_queue_model.clear())

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent):
        # Delete items from Auto Queue
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                indices = self.auto_queue.selectionModel().selectedRows()
                for index in sorted(indices):
                    self.auto_queue_model.removeRow(index.row())
        return super().eventFilter(source, event)