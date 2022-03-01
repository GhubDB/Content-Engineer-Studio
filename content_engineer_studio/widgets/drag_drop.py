from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap


class DragDrop(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.drag_drop_layout = QVBoxLayout()

        self.analysis_img = QPixmap("icons\drag_drop_analysis.ico")
        self.testing_img = QPixmap("icons\drag_drop_testing.ico")

        self.drop_1 = QLabel()
        self.drop_2 = QLabel()
        self.drop_1.setPixmap(self.analysis_img)
        self.drop_1.setScaledContents(True)
        self.drop_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.drop_2.setPixmap(self.testing_img)
        self.drop_2.setScaledContents(True)
        self.drop_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

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
        # self.show()
