# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Me\Dropbox\Python\content_engineer_studio\pqt_test_designs\testing_suite.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1375, 629)
        self.chat = QtWidgets.QTableWidget(Form)
        self.chat.setGeometry(QtCore.QRect(52, 10, 656, 577))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chat.sizePolicy().hasHeightForWidth())
        self.chat.setSizePolicy(sizePolicy)
        self.chat.setMinimumSize(QtCore.QSize(650, 0))
        self.chat.setFrameShape(QtWidgets.QFrame.Panel)
        self.chat.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chat.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chat.setObjectName("chat")
        self.chat.setColumnCount(0)
        self.chat.setRowCount(0)
        self.chat.horizontalHeader().setVisible(False)
        self.chat.verticalHeader().setVisible(False)
        self.sidebar = QtWidgets.QTableView(Form)
        self.sidebar.setGeometry(QtCore.QRect(10, 10, 35, 612))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidebar.sizePolicy().hasHeightForWidth())
        self.sidebar.setSizePolicy(sizePolicy)
        self.sidebar.setMinimumSize(QtCore.QSize(35, 0))
        self.sidebar.setMaximumSize(QtCore.QSize(35, 16777215))
        self.sidebar.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.sidebar.setFrameShape(QtWidgets.QFrame.Panel)
        self.sidebar.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sidebar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sidebar.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.sidebar.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sidebar.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.sidebar.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.sidebar.setObjectName("sidebar")
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(730, 50, 531, 481))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.sidebar.setAccessibleName(_translate("Form", "sidebar_css"))
