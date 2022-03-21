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
from utils.model_test import ModelTest


class FaqSearchBoxContainer(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.gui = parent.gui
        self.suite = parent

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Search Text input
        self.searchbar_layout = QHBoxLayout()
        self.searchbar_layout.setContentsMargins(0, 0, 0, 0)
        self.searchbar = QtWidgets.QLineEdit()
        self.searchbar.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchbar.setFont(font)
        self.searchbar.setObjectName("searchbar")
        self.searchbar_layout.addWidget(self.searchbar)
        self.main_layout.addLayout(self.searchbar_layout, 0, 0)

        # Column select Combobox
        self.search_column_select = QtWidgets.QComboBox()
        self.search_column_select.setObjectName("search_column_select")
        self.searchbar_layout.addWidget(self.search_column_select)

        # FAQ display Tableview
        self.search_box = FaqDisplayBox(parent=self)
        self.main_layout.addWidget(self.search_box, 1, 0)

        # Connecting Functions
        self.searchbar.textChanged.connect(
            lambda: self.search_box.setMinimumHeight(500)
        )
        self.searchbar.editingFinished.connect(
            lambda: self.search_box.setMinimumHeight(100)
        )

        # Initializing FAQ search window item model
        model = QStandardItemModel(len(self.faq_df.index), len(self.faq_df.columns))
        for idx, _ in self.faq_df.iterrows():
            for i, _ in enumerate(self.faq_df.columns):
                item = QStandardItem(self.faq_df.iloc[idx, i])
                model.setItem(idx, i, item)  # check this
        self.faq_auto_search_model = QSortFilterProxyModel()
        self.faq_auto_search_model.setSourceModel(model)
        self.faq_auto_search_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.faq_auto_search_model.setFilterKeyColumn(-1)
        self.search_box.installEventFilter(self)
        self.gui.search_box_3.installEventFilter(self)

        # Adding search box
        self.populate_search_column_select()
        self.search_box.setModel(self.faq_auto_search_model)
        self.gui.search_box_3.setModel(self.faq_auto_search_model)
        self.gui.search_box_3.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.searchbar.textChanged.connect(self.faq_auto_search_model.setFilterRegExp)
        self.gui.searchbar_3.textChanged.connect(
            self.faq_auto_search_model.setFilterRegExp
        )
        self.search_column_select.currentIndexChanged.connect(self.populate_search_box)
        self.gui.search_column_select_3.currentIndexChanged.connect(
            self.populate_search_box
        )
        self.populate_search_box()

    def populate_search_box(self):
        """
        Populates the search box with values from FAQ excel sheet
        """
        # Synchronize selectors
        page = self.stackedWidget.currentIndex()
        if page == 0:
            index = self.search_column_select.currentIndex()
            self.search_column_select_2.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 1:
            index = self.search_column_select_2.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 3:
            index = self.search_column_select_3.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_2.setCurrentIndex(index)

        # Set table column to filter by
        try:
            if index == len(self.faq_df.columns):
                # Set to filter by all columns
                self.faq_auto_search_model.setFilterKeyColumn(-1)
            else:
                self.faq_auto_search_model.setFilterKeyColumn(index)
        except UnboundLocalError as e:
            pass

        # Show/hide columns according to current selection
        if (page == 0 or page == 1) and index != len(self.faq_df.columns):
            for i in range(0, len(self.faq_df.index)):
                if i != index:
                    self.search_box.hideColumn(
                        i
                    ) if page == 0 else self.search_box_2.hideColumn(i)
                else:
                    self.search_box.showColumn(
                        i
                    ) if page == 0 else self.search_box_2.showColumn(i)

    def populate_search_column_select(self):
        """
        Set model for FAQ search selector
        """
        model = QStandardItemModel(len(self.faq_df.columns), 0)
        for idx, item in enumerate(list(self.faq_df.columns.values)):
            item = QStandardItem(item)
            model.setItem(idx, 0, item)

        # For searching all columns
        item = QStandardItem("Search in all columns")
        model.setItem(len(self.faq_df.columns), 0, item)
        self.search_column_select.setModel(model)
        self.search_column_select_3.setModel(model)


class FaqDisplayBox(QTableView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.gui = parent.gui

        # Set-up
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
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
        self.setObjectName("search_box")
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:

        # Show FAQ search table
        if e.button() == Qt.RightButton:
            index = self.selectionModel().currentIndex()
            value = index.sibling(index.row(), index.column()).data()
            self.gui.stackedWidget.setCurrentWidget(self.faq)
            self.searchbar_3.setText(value)

        return super().mouseReleaseEvent(e)
