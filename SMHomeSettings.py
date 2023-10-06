# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/SMHomeSettings.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(518, 288)
        SettingsDialog.setMaximumSize(QtCore.QSize(16777215, 16777212))
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, -1, -1, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.FilterFGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.FilterFGBtn.setAutoDefault(False)
        self.FilterFGBtn.setObjectName("FilterFGBtn")
        self.gridLayout.addWidget(self.FilterFGBtn, 0, 2, 1, 1)
        self.FilterTest = QtWidgets.QPlainTextEdit(SettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FilterTest.sizePolicy().hasHeightForWidth())
        self.FilterTest.setSizePolicy(sizePolicy)
        self.FilterTest.setMaximumSize(QtCore.QSize(16777215, 45))
        self.FilterTest.setReadOnly(False)
        self.FilterTest.setBackgroundVisible(False)
        self.FilterTest.setObjectName("FilterTest")
        self.gridLayout.addWidget(self.FilterTest, 0, 1, 1, 1)
        self.SendTest = QtWidgets.QPlainTextEdit(SettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SendTest.sizePolicy().hasHeightForWidth())
        self.SendTest.setSizePolicy(sizePolicy)
        self.SendTest.setMaximumSize(QtCore.QSize(16777215, 45))
        self.SendTest.setObjectName("SendTest")
        self.gridLayout.addWidget(self.SendTest, 1, 1, 1, 1)
        self.label_1 = QtWidgets.QLabel(SettingsDialog)
        self.label_1.setObjectName("label_1")
        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.SendFGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.SendFGBtn.setAutoDefault(False)
        self.SendFGBtn.setObjectName("SendFGBtn")
        self.gridLayout.addWidget(self.SendFGBtn, 1, 2, 1, 1)
        self.SendBGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.SendBGBtn.setAutoDefault(False)
        self.SendBGBtn.setObjectName("SendBGBtn")
        self.gridLayout.addWidget(self.SendBGBtn, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(SettingsDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.FilterBGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.FilterBGBtn.setAutoDefault(False)
        self.FilterBGBtn.setObjectName("FilterBGBtn")
        self.gridLayout.addWidget(self.FilterBGBtn, 0, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(SettingsDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.RcvTest = QtWidgets.QPlainTextEdit(SettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RcvTest.sizePolicy().hasHeightForWidth())
        self.RcvTest.setSizePolicy(sizePolicy)
        self.RcvTest.setMaximumSize(QtCore.QSize(16777215, 45))
        self.RcvTest.setObjectName("RcvTest")
        self.gridLayout.addWidget(self.RcvTest, 2, 1, 1, 1)
        self.RcvFGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.RcvFGBtn.setAutoDefault(False)
        self.RcvFGBtn.setObjectName("RcvFGBtn")
        self.gridLayout.addWidget(self.RcvFGBtn, 2, 2, 1, 1)
        self.RcvBGBtn = QtWidgets.QPushButton(SettingsDialog)
        self.RcvBGBtn.setAutoDefault(False)
        self.RcvBGBtn.setObjectName("RcvBGBtn")
        self.gridLayout.addWidget(self.RcvBGBtn, 2, 3, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.cancel_btn = QtWidgets.QPushButton(SettingsDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_7.addWidget(self.cancel_btn)
        self.ok_btn = QtWidgets.QPushButton(SettingsDialog)
        self.ok_btn.setObjectName("ok_btn")
        self.horizontalLayout_7.addWidget(self.ok_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(SettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Dialog"))
        self.FilterFGBtn.setText(_translate("SettingsDialog", "SetFG"))
        self.FilterTest.setPlainText(_translate("SettingsDialog", "quick brown fox jumps over the lazy dog"))
        self.SendTest.setPlainText(_translate("SettingsDialog", "quick brown fox jumps over the lazy dog"))
        self.label_1.setText(_translate("SettingsDialog", "Filtered packet:"))
        self.SendFGBtn.setText(_translate("SettingsDialog", "SetFG"))
        self.SendBGBtn.setText(_translate("SettingsDialog", "SetBG"))
        self.label.setText(_translate("SettingsDialog", "Send Packet"))
        self.FilterBGBtn.setText(_translate("SettingsDialog", "SetBG"))
        self.label_2.setText(_translate("SettingsDialog", "Received Packet"))
        self.RcvTest.setPlainText(_translate("SettingsDialog", "quick brown fox jumps over the lazy dog"))
        self.RcvFGBtn.setText(_translate("SettingsDialog", "SetFG"))
        self.RcvBGBtn.setText(_translate("SettingsDialog", "SetBG"))
        self.cancel_btn.setText(_translate("SettingsDialog", "Cancel"))
        self.ok_btn.setText(_translate("SettingsDialog", "OK"))