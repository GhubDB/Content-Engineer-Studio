import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QTableView, QWidget


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
        self.searchbar.setPlaceholderText("Search FAQs")
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
        self.search_column_select.currentIndexChanged.connect(
            self.gui.update_search_box
        )


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
            self.gui.central_stacked_widget.setCurrentWidget(self.gui.faq_search_tab)
            self.gui.faq_search_tab.searchbar.setText(value)

        return super().mouseReleaseEvent(e)
