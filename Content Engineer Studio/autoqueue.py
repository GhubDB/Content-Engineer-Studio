from PyQt5 import QtWidgets, QtGui


class AutoQueue(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def resetColors(self):
        for row in self.auto_queue.rowCount():
            item = self.auto_queue.cellWidget(row, 0)
            item.setBackground(QtGui.QColor(70, 70, 70))