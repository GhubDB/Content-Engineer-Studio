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

from qtstylish import qtstylish

from widgets.analysis_suite import AnalysisSuite
from widgets.testing_suite import TestingSuite

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    win = TestingSuite()
    win.resize(1920, 1080)
    win.show()
    sys.exit(app.exec_())
