from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QCursor, QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class DragDrop(QWidget):
    """
    This class handles setting the dataframe for analysis/testing via drag & drop
    """

    def __init__(self, parent):
        super().__init__()

        self.drag_drop_layout = QVBoxLayout()

        self.analysis_img = QPixmap("icons\drag_drop_analysis.ico")
        self.testing_img = QPixmap("icons\drag_drop_testing.ico")

        self.drop_1 = DragDropLabel(name="analysis", parent=parent)
        self.drop_2 = DragDropLabel(name="testing", parent=parent)

        self.drop_1.setPixmap(self.analysis_img)
        self.drop_2.setPixmap(self.testing_img)

        self.drag_drop_layout.addWidget(self.drop_1)
        self.drag_drop_layout.addWidget(self.drop_2)
        self.setLayout(self.drag_drop_layout)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(250, 196))
        self.setMinimumSize(QSize(150, 196))


class DragDropLabel(QLabel):
    """
    This is a clickable label that the user can drop a dataframe onto.
    dropping a dataframe onto it sets the working dataframe for the mode specified on the label
    clicking on the label switches the analyis/testing widget
    """

    def __init__(self, name: str, parent: QWidget):
        super().__init__(name, parent)
        self.name = name
        self.gui = parent
        self.setAcceptDrops(True)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.installEventFilter(self)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def dragEnterEvent(self, event: QEvent):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QEvent):
        # Check if the dropped item is a valid dataframe
        if event.mimeData().hasFormat("text/plain"):
            if self.name == "analysis":
                self.setText("Analysis:\n" + event.mimeData().text())
                self.setStyleSheet("border: 4px solid #007ce5;")
            elif self.name == "testing":
                self.setText("Testing:\n" + event.mimeData().text())
                self.setStyleSheet("border: 4px solid #007ce5;")
            else:
                raise "Not a valid Dataframe"

            # Add styling and text to drop label to show that the item has been added
            font = QFont("MS Shell Dlg 2", 10, QFont.Bold)
            self.setFont(font)
            # self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
            self.setWordWrap(True)

            # set up the working dataframe for analysis or testing
            self.gui.set_df(df_title=event.mimeData().text(), mode=self.name)

    def eventFilter(self, source, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if source.name == "analysis":
                self.gui.central_stacked_widget.setCurrentIndex(0)
            else:
                self.gui.central_stacked_widget.setCurrentIndex(1)
        return super().eventFilter(source, event)
