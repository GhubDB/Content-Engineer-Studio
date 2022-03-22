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
    QTableView,
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


class FaqSearchTabContainer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.gui = parent

        self.setObjectName("faq_search_tab")
        self.main_grid = QtWidgets.QGridLayout(self)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setObjectName("main_grid")

        # Searchbar
        self.searchbar = QtWidgets.QLineEdit(self)
        self.searchbar.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchbar.setFont(font)
        self.searchbar.setObjectName("searchbar")
        self.main_grid.addWidget(self.searchbar, 0, 0, 1, 1)

        # search_column_select
        self.search_column_select = QtWidgets.QComboBox()
        self.search_column_select.setMinimumSize(QtCore.QSize(150, 0))
        self.search_column_select.setObjectName("search_column_select")
        self.main_grid.addWidget(self.search_column_select, 0, 1, 1, 1)

        # close_faq
        self.close_faq = QtWidgets.QPushButton()
        self.close_faq.setMaximumSize(QtCore.QSize(60, 16777215))
        self.close_faq.setObjectName("close_faq")
        self.main_grid.addWidget(self.close_faq, 0, 2, 1, 1)

        # search_box
        self.search_box = FaqDisplay(parent=self)
        self.main_grid.addWidget(self.search_box, 1, 0, 1, 3)

        self.search_column_select.currentIndexChanged.connect(
            self.gui.update_search_box
        )


class FaqDisplay(QTableView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.gui = parent.gui
        self.container = parent

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setObjectName("search_box")
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            index = self.selectionModel().currentIndex()
            if not index.isValid():
                return super().mouseReleaseEvent(e)
            value = index.sibling(index.row(), index.column()).data()
            self.container.search_column_select.setCurrentIndex(index.column())
            self.gui.analysis_suite.faq_search_box.searchbar.setText(
                value
            ) if self.gui.current_work_area == 0 else self.gui.testing_suite.faq_search_box.searchbar.setText(
                value
            )

            self.gui.stackedWidget.setCurrentIndex(self.gui.current_work_area)
            self.gui.populate_search_box()
            self.gui.testing_suite.faq_search_box.search_box.setMinimumHeight(100)
            self.gui.testing_suite.faq_search_box.search_box.setMinimumHeight(100)
        return super().mouseReleaseEvent(e)
