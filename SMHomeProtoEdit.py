# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/SMHomeProtoEdit.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProtocolEditDialog(object):
    def setupUi(self, ProtocolEditDialog):
        ProtocolEditDialog.setObjectName("ProtocolEditDialog")
        ProtocolEditDialog.setWindowModality(QtCore.Qt.NonModal)
        ProtocolEditDialog.resize(799, 531)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProtocolEditDialog.sizePolicy().hasHeightForWidth())
        ProtocolEditDialog.setSizePolicy(sizePolicy)
        ProtocolEditDialog.setMinimumSize(QtCore.QSize(0, 0))
        ProtocolEditDialog.setBaseSize(QtCore.QSize(0, 0))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ProtocolEditDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.file_name = QtWidgets.QLabel(ProtocolEditDialog)
        self.file_name.setObjectName("file_name")
        self.gridLayout.addWidget(self.file_name, 0, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(ProtocolEditDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(ProtocolEditDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.proto_name = QtWidgets.QLineEdit(ProtocolEditDialog)
        self.proto_name.setObjectName("proto_name")
        self.gridLayout.addWidget(self.proto_name, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(ProtocolEditDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(ProtocolEditDialog)
        self.pushButton.setAutoDefault(False)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 4, 1, 1)
        self.proto_descr = QtWidgets.QPlainTextEdit(ProtocolEditDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.proto_descr.sizePolicy().hasHeightForWidth())
        self.proto_descr.setSizePolicy(sizePolicy)
        self.proto_descr.setMaximumSize(QtCore.QSize(16777215, 40))
        self.proto_descr.setObjectName("proto_descr")
        self.gridLayout.addWidget(self.proto_descr, 1, 1, 1, 4)
        self.gridLayout.setColumnStretch(3, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.frame_id = QtWidgets.QTabWidget(ProtocolEditDialog)
        self.frame_id.setTabBarAutoHide(False)
        self.frame_id.setObjectName("frame_id")
        self.frameid_tab = QtWidgets.QWidget()
        self.frameid_tab.setObjectName("frameid_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameid_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 12, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QtWidgets.QLabel(self.frameid_tab)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.label_4 = QtWidgets.QLabel(self.frameid_tab)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.gap_selector = QtWidgets.QComboBox(self.frameid_tab)
        self.gap_selector.setMinimumSize(QtCore.QSize(200, 0))
        self.gap_selector.setObjectName("gap_selector")
        self.horizontalLayout_2.addWidget(self.gap_selector)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.add_slice_btn = QtWidgets.QPushButton(self.frameid_tab)
        self.add_slice_btn.setAutoDefault(False)
        self.add_slice_btn.setObjectName("add_slice_btn")
        self.horizontalLayout_2.addWidget(self.add_slice_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.frameid_slices_tbl = QtWidgets.QTableView(self.frameid_tab)
        self.frameid_slices_tbl.setMidLineWidth(1)
        self.frameid_slices_tbl.setAlternatingRowColors(True)
        self.frameid_slices_tbl.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.frameid_slices_tbl.setObjectName("frameid_slices_tbl")
        self.frameid_slices_tbl.horizontalHeader().setCascadingSectionResizes(True)
        self.frameid_slices_tbl.horizontalHeader().setStretchLastSection(True)
        self.frameid_slices_tbl.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.frameid_slices_tbl)
        self.frame_id.addTab(self.frameid_tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.frame_id.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.frame_id)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancel_btn = QtWidgets.QPushButton(ProtocolEditDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.saveas_btn = QtWidgets.QPushButton(ProtocolEditDialog)
        self.saveas_btn.setAutoDefault(False)
        self.saveas_btn.setObjectName("saveas_btn")
        self.horizontalLayout.addWidget(self.saveas_btn)
        self.save_btn = QtWidgets.QPushButton(ProtocolEditDialog)
        self.save_btn.setAutoDefault(False)
        self.save_btn.setObjectName("save_btn")
        self.horizontalLayout.addWidget(self.save_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(ProtocolEditDialog)
        self.frame_id.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ProtocolEditDialog)

    def retranslateUi(self, ProtocolEditDialog):
        _translate = QtCore.QCoreApplication.translate
        ProtocolEditDialog.setWindowTitle(_translate("ProtocolEditDialog", "Edit protcols slices"))
        self.file_name.setText(_translate("ProtocolEditDialog", "The file"))
        self.label_2.setText(_translate("ProtocolEditDialog", "Description"))
        self.label.setText(_translate("ProtocolEditDialog", "Protocol name"))
        self.label_3.setText(_translate("ProtocolEditDialog", "File name:"))
        self.pushButton.setText(_translate("ProtocolEditDialog", "Load"))
        self.label_5.setText(_translate("ProtocolEditDialog", "Total bits len 29 "))
        self.label_4.setText(_translate("ProtocolEditDialog", "Select gap foe new slice"))
        self.add_slice_btn.setText(_translate("ProtocolEditDialog", "Insert new slice"))
        self.frame_id.setTabText(self.frame_id.indexOf(self.frameid_tab), _translate("ProtocolEditDialog", "Frame ID"))
        self.frame_id.setTabText(self.frame_id.indexOf(self.tab_2), _translate("ProtocolEditDialog", "Frame Data"))
        self.cancel_btn.setText(_translate("ProtocolEditDialog", "Cancel"))
        self.saveas_btn.setText(_translate("ProtocolEditDialog", "Save As"))
        self.save_btn.setText(_translate("ProtocolEditDialog", "Save"))