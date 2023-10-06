import sys

from PyQt5.QtWidgets import QMessageBox

import SMH
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
import logging
from logging import StreamHandler, Formatter

from SMH_Proto import ProtoSlice, CustomProto
from SMHomeFilterEdit import Ui_FilterDialog

import types

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class Communicate(QObject):
    ok_signal = pyqtSignal(dict, name='add')


class FilterEditDialog(Ui_FilterDialog):
    ok_signal = pyqtSignal(dict, name='add')

    # SMH.FR_ID_TYPE_BASE = 0
    # SMH.FR_ID_TYPE_EXT = 1
    # SMH.ACTION_WAIT = 0
    # SMH.ACTION_SEND = 1

    def __init__(self, *args, **kwargs):
        super(FilterEditDialog, self).__init__(*args, **kwargs)
        self.comm = Communicate()
        self.parentWidget = None
        self.RID = 0

        self.name = ""
        self.descr = ""
        self.action = SMH.ACTION_SEND
        self.tout = 0
        self.id_f_bits = []
        self.id_m_bits = []
        self.data_m_bits = [[0 for x in range(0, 8)] for y in range(0, 8)]
        self.data_f_bits = [[0 for x in range(0, 8)] for y in range(0, 8)]
        self.frameID = 0
        self.frameID_mask = 0x1FFFFFFF
        self.is_IDExt = True
        self.dataLen = 0
        self.dataAr = [0] * 8
        self.dataAr_mask = [0] * 8
        self.use_data = False

        self._is_id_changing_ = False
        self._is_data_changing_ = False
        self.isMask = True
        self.proto: CustomProto = None
        self.sliced_id = {}
        self.proto_slice_control = []

        for i in range(0, 29):
            self.id_f_bits.append("f{:02d}".format(i))
            self.id_m_bits.append("m{:02d}".format(i))

        for x in range(0, 8):
            for y in range(0, 8):
                self.data_f_bits[x][y] = "DB{:1d}{:1d}".format(x + 1, y)
                self.data_m_bits[x][y] = "DF{:1d}{:1d}".format(x + 1, y)

        logger.info("Init")

    def setupUi(self, dialog):
        self.parentWidget = dialog
        super(FilterEditDialog, self).setupUi(dialog)
        dialog.c = False
        # self.buttonBox.accepted.connect(self.accept)
        self.useMask.setChecked(self.isMask)
        self.set_type(self.action)
        self.set_frameIDType(self.is_IDExt)
        self.set_frameID(self.frameID, self.frameID_mask)
        self.set_data_len(self.dataLen)
        self.set_data_bytes(self.dataAr,  self.dataAr_mask)

        self.timeout.setText(str(self.tout))
        self.ParentRuleID.addItem("0")
        self.ParentRuleID.setCurrentText("0")
        self.ParentRuleID.setEditable(False)
        self.useData.setChecked(self.use_data)
        self.ch_UseData

        # Assign UI property to DATA and MASK
        for x in range(0, 8):
            for y in range(0, 8):
                # print("Data F bits {} {} = {}".format(x, y, self.data_f_bits[x][y]))
                self.__dict__[self.data_f_bits[x][y]].setMinimumSize(QtCore.QSize(38, 25))
                self.__dict__[self.data_f_bits[x][y]].setAlignment(QtCore.Qt.AlignCenter)
                self.__dict__[self.data_f_bits[x][y]].valueChanged.connect(self._ch_data_byte_evt)

                # self.__dict__[self.data_m_bits[x][y]].setValue(1)
                self.__dict__[self.data_m_bits[x][y]].setMinimumSize(QtCore.QSize(38, 25))
                self.__dict__[self.data_m_bits[x][y]].setAlignment(QtCore.Qt.AlignCenter)
                self.__dict__[self.data_m_bits[x][y]].valueChanged.connect(self._ch_data_byte_evt)

        # Assign UI property to ID and mask
        # self.set_frameID(0x00, 0xFFFFFFFF)
        for i in range(0, 29):
            # self.__dict__[self.id_m_bits[i]].setValue(1)
            self.__dict__[self.id_f_bits[i]].valueChanged.connect(self._ch_frameId_evt)
            self.__dict__[self.id_m_bits[i]].valueChanged.connect(self._ch_frameId_evt)

        # Assign Events
        self.data_len_spin.valueChanged.connect(lambda: self.set_data_len(self.data_len_spin.value()))
        self.frameid_hex_edit.editingFinished.connect(lambda: self._ch_frameId_hex_evt("base"))
        # self.frameidmask_hex_edit.returnPressed.connect(lambda: self._ch_frameId_hex_evt("mask"))
        self.frameidmask_hex_edit.editingFinished.connect(lambda: self._ch_frameId_hex_evt("mask"))

        self.frtype_std_rbtn.clicked.connect(lambda: self.set_frameIDType(False))
        self.frtype_ext_rbtn.clicked.connect(lambda: self.set_frameIDType(True))
        self.wait_rbtn.clicked.connect(lambda: self.set_type(SMH.ACTION_WAIT))
        self.send_rbtn.clicked.connect(lambda: self.set_frameIDType(SMH.ACTION_SEND))

        # self.clear_id_btn.clicked.connect(lambda: self.commlear_frameID())
        self.clear_id_btn.clicked.connect(self.frameid_hex_edit.clear)

        self.useMask.stateChanged.connect(self.ch_UseMask)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)
        self.RuleName.textChanged[str].connect(self._ch_name_evt)
        self.RuleDescr.textChanged[str].connect(self._ch_descr_evt)
        self.timeout.textChanged[str].connect(self._ch_tout_evt)
        self.useData.stateChanged.connect(self.ch_UseData)
        # self.set_frameIDType(SMH.FR_ID_TYPE_EXT)

        if self.proto is None:
            logger.debug("Proto is not defined.")
            self.proto_id.setEnabled(False)

    def setup_proto_UI(self, proto: CustomProto):
        """
        Generate protocol view tabs input fields
        :param proto:
        :return:
        """

        self.proto = proto
        self.proto_id.setEnabled(True)
        row_id = 0

        for proto_slice in proto:

            # slice_short = proto_slice.short
            # logger.debug("Generate input fields for proto slice = %s", proto_slice.name)

            #  Slice name
            row_ar: list = [QtWidgets.QLabel(self.proto_id)]
            row_ar[-1].setObjectName("label_100"+proto_slice.short)
            row_ar[-1].setText(proto_slice.name+" ("+proto_slice.short+")")
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 0, 1, 1)

            # Start bit lbl
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_101"+proto_slice.short)
            row_ar[-1].setText("Start bit:")
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 1, 1, 1)

            # Start bit value
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_102"+proto_slice.short)
            row_ar[-1].setText(str(proto_slice.start))
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 2, 1, 1)

            # Spacer
            row_ar.append(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
            self.proto_view_layout.addItem(row_ar[-1], row_id, 3, 1, 1)

            # Bit len lbl
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_103"+proto_slice.short)
            row_ar[-1].setText("Bits len:")
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 4, 1, 1)

            # Bit len value
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_104"+proto_slice.short)
            row_ar[-1].setText(str(proto_slice.len))
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 5, 1, 1)

            # Spacer
            row_ar.append(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
            self.proto_view_layout.addItem(row_ar[-1], row_id, 6, 1, 1)

            # Value LBL
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_105"+proto_slice.short)
            row_ar[-1].setText("Value")
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 7, 1, 1)

            #  Slice hex value
            slice_edit_widget = QtWidgets.QLineEdit(self.proto_id)
            row_ar.append(slice_edit_widget)
            slice_edit_widget.setObjectName("lineEdit_106"+proto_slice.short)
            slice_edit_widget.editingFinished.connect(lambda: self._ch_frameId_proto_evt("base"))
            self.proto_slice_control.append(slice_edit_widget)
            self.proto_view_layout.addWidget(slice_edit_widget, row_id, 8, 1, 1)

            row_ar.append(QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
            self.proto_view_layout.addItem(row_ar[-1], row_id, 9, 1, 1)

            # mask lbl
            row_ar.append(QtWidgets.QLabel(self.proto_id))
            row_ar[-1].setObjectName("label_110"+proto_slice.short)
            row_ar[-1].setText("Мask")
            self.proto_view_layout.addWidget(row_ar[-1], row_id, 10, 1, 1)

            #  Slice hex value
            slmask_edit_widget = QtWidgets.QLineEdit(self.proto_id)
            row_ar.append(slmask_edit_widget)
            slmask_edit_widget.setObjectName("lineEdit_111"+proto_slice.short)
            slmask_edit_widget.editingFinished.connect(lambda: self._ch_frameId_proto_evt("mask"))
            self.proto_view_layout.addWidget(slmask_edit_widget, row_id, 11, 1, 1)
            row_id += 1

            self.sliced_id[proto_slice.short] = {
                "name": proto_slice.short,
                "slice": proto_slice,
                "base_widget": slice_edit_widget,
                "mask_widget": slmask_edit_widget
            }

        self.proto_view_layout.setColumnStretch(6, 1)
        self.set_proto_val(self.frameID, self.frameID_mask)

    def _ch_frameId_proto_evt(self, val_type):
        value = 0
        for sl_short in self.sliced_id.keys():
            if val_type == "base":
                value = int(self.sliced_id[sl_short]["base_widget"].text(), 16)
                self.frameID = self.proto.get_slice(sl_short).ins_val(self.frameID, value)
            else:
                value = int(self.sliced_id[sl_short]["mask_widget"].text(), 16)
                self.frameID_mask = self.proto.get_slice(sl_short).ins_val(self.frameID_mask, value)
        self.set_frameID(self.frameID, self.frameID_mask)

    def set_proto_val(self, frameID, frameID_mask):

        for sl_short in self.sliced_id.keys():
            sl: ProtoSlice = self.sliced_id[sl_short]["slice"]
            format_line = "0x{:0" + str(int((sl.len/4)+0.9)) + "X}"
            out_str = format_line.format(sl.ext_val(frameID))
            self.sliced_id[sl_short]["base_widget"].setText(out_str)
            out_str = format_line.format(sl.ext_val(frameID_mask))
            self.sliced_id[sl_short]["mask_widget"].setText(out_str)

    def _ch_name_evt(self, text: str):
        self.name = text

    def _ch_descr_evt(self, text: str):
        self.descr = text

    def _ch_tout_evt(self, text: str):
        self.tout = int(text)

    def setupData(self, data: dict):
        self.set_name(data[SMH.FL_NAME])
        self.set_descr(data[SMH.FL_DESCR])
        self.set_ruleID(data[SMH.FL_ID])
        self.set_parentRuleID(data[SMH.FL_PARENT_ID])
        self.timeout.setText(str(data[SMH.FL_TIMEOUT]))
        self.set_type(data[SMH.FL_ACTION])

        base_frame = data[SMH.FL_FILTER_FR]
        mask_frame = data[SMH.FL_MASK_FR]

        if data[SMH.FL_MASK_EMPTY]:
            self.useMask.setChecked(False)
        else:
            self.useMask.setChecked(True)

        self.isMask = not data[SMH.FL_MASK_EMPTY]

        self.set_frameIDType(base_frame[SMH.FR_ID_EXT])
        self.set_frameID(base_frame[SMH.FR_ID], mask_frame[SMH.FR_ID])

        self.set_data_len(base_frame[SMH.FR_DATA_LEN])
        self.useData.setChecked(data[SMH.FL_USE_DATA])
        # if self.use_data:
        self.set_data_bytes(base_frame[SMH.FR_DATA_AR], mask_frame[SMH.FR_DATA_AR])

        logger.info("Set data: {}".format(data))

    def accept(self):
        # Check Rule name exist
        if self.RuleName.text() == "":
            logger.debug("The name field empty.")
            # error_dialog = QtWidgets.QErrorMessage(self.parentWidget)
            # error_dialog.showMessage('Rule name empty!')
            msgBox = QMessageBox(self.parentWidget)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Rule name empty!")
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(QMessageBox.Ok)
            # msgBox.buttonClicked.connect(msgButtonClick)
            returnValue = msgBox.exec()
            return

        data_frame = {
            SMH.FR_ID_EXT: self.is_IDExt,
            SMH.FR_ID: self.frameID,
            SMH.FR_DATA_LEN: self.dataLen,
            SMH.FR_DATA_AR: self.dataAr
        }
        # mask_frame = None

        mask_frame = {
            SMH.FR_ID_EXT: self.is_IDExt,
            SMH.FR_ID: self.frameID_mask,
            SMH.FR_DATA_LEN: self.dataLen,
            SMH.FR_DATA_AR: self.dataAr_mask
        }

        if not self.isMask:
            mask_frame[SMH.FR_ID] = 0x1FFFFFFF

        data = {
            SMH.FL_ID: self.RID,
            SMH.FL_NAME: self.name,
            SMH.FL_DESCR: self.descr,

            SMH.FL_PARENT_ID: int(self.ParentRuleID.currentText()),
            SMH.FL_FILTER_FR: data_frame,
            SMH.FL_MASK_FR: mask_frame,
            SMH.FL_ACTION: SMH.ACT_TEXT_WAIT if self.action == SMH.ACTION_WAIT else SMH.ACT_TEXT_SEND,
            SMH.FL_TIMEOUT: self.tout,
            SMH.FL_MASK_EMPTY: not self.isMask
        }

        logger.info("SAVED Data: {}".format(data))
        self.comm.ok_signal.emit(data)
        self.parentWidget.close()

    def close(self):
        self.parentWidget.close()

    def set_ruleID(self, RID):
        self.RID = RID
        self.RuleID.setText(str(RID))

    def set_parentRuleID(self, PRuleId):
        self.ParentRuleID.addItem(str(PRuleId))
        self.ParentRuleID.setCurrentText(str(PRuleId))

    def ch_UseData(self):
        if self.useData.isChecked():
            self.use_data = True
            self.data_len_spin.setDisabled(False)
            for x in range(0, self.dataLen):
                for y in range(0, 8):
                    self.__dict__[self.data_f_bits[x][y]].setDisabled(False)
                    self.__dict__[self.data_m_bits[x][y]].setDisabled(False)
        else:
            self.use_data = False
            self.data_len_spin.setDisabled(True)
            for x in range(0, 8):
                for y in range(0, 8):
                    self.__dict__[self.data_f_bits[x][y]].setDisabled(True)
                    self.__dict__[self.data_m_bits[x][y]].setDisabled(True)

    def ch_UseMask(self):
        if self.useMask.isChecked():
            self.isMask = True
            for i in range(0, 16):
                self.__dict__[self.id_m_bits[i]].setDisabled(False)
            # self.set_frameIDType(self.is_IDExt)
            # self.set_data_len(self.dataLen)
            for x in range(0, self.dataLen):
                for y in range(0, 8):
                    self.__dict__[self.data_m_bits[x][y]].setDisabled(True)

        else:
            self.isMask = False
            for i in range(0, 29):
                self.__dict__[self.id_m_bits[i]].setDisabled(True)
            for x in range(0, self.dataLen):
                for y in range(0, 8):
                    self.__dict__[self.data_m_bits[x][y]].setDisabled(True)

    def set_frameIDType(self, is_ID_ext):
        logger.debug("Change frame type to %s",
                     "Ext ID" if is_ID_ext else "Base ID")
        self.is_IDExt = is_ID_ext
        if is_ID_ext:
            if self.frtype_std_rbtn.isChecked():
                self.commlear_frameID()
            self.frtype_ext_rbtn.setChecked(True)
            self.frtype_std_rbtn.setChecked(False)
            for i in range(16, 29):
                self.__dict__[self.id_f_bits[i]].setEnabled(True)
                self.__dict__[self.id_m_bits[i]].setEnabled(True)

        else:
            if self.frtype_ext_rbtn.isChecked():
                self.commlear_frameID()
            self.frtype_ext_rbtn.setChecked(False)
            self.frtype_std_rbtn.setChecked(True)
            for i in range(16, 29):
                self.__dict__[self.id_f_bits[i]].setDisabled(True)
                self.__dict__[self.id_m_bits[i]].setDisabled(True)

    def get_frameIDType(self):
            return self.is_IDExt

    def set_name(self, name):
        self.RuleName.setText(name)

    def get_name(self):
        return self.name

    def set_descr(self, txt):
        self.RuleDescr.setText(txt)

    def get_descr(self, txt):
        return self.descr

    def set_frameID(self, frameID, frameID_mask):
        if self._is_id_changing_:
            return
        self._is_id_changing_ = True
        # self.IDFrame.blockSignals(True)
        logger.debug("Set frame id (%s) = 0x%08X, mask 0x%08X", self.is_IDExt, frameID, frameID_mask)

        self.frameID = frameID
        self.frameID_mask = frameID_mask

        if self.is_IDExt:
            fid_array = list("{:029b}".format(frameID))
            fid_mask_array = list("{:029b}".format(frameID_mask))
            # logger.debug("ID bits %s, Mask bits %s", "".join(fid_array[0:29]), "".join(fid_mask_array[0:29]))
            for i in range(29):
                self.__dict__[self.id_f_bits[i]].setValue(int(fid_array[28 - i]))
                self.__dict__[self.id_m_bits[i]].setValue(int(fid_mask_array[28 - i]))
            self.frameid_hex_edit.setText("0x{:08X}".format(frameID))
            self.frameidmask_hex_edit.setText("0x{:08X}".format(frameID_mask))
        else:
            fid_array = list("{:016b}".format(frameID))
            fid_mask_array = list("{:016b}".format(frameID_mask))
            for i in range(0, 16):
                self.__dict__[self.id_f_bits[i]].setValue(int(fid_array[16 - i]))
                self.__dict__[self.id_m_bits[i]].setValue(int(fid_mask_array[16 - i]))
            self.frameid_hex_edit.setText("0x{:04X}".format(frameID))
            self.frameidmask_hex_edit.setText("0x{:04X}".format(frameID_mask))

        if self.proto is not None:
            logger.debug("Frame ID by proto %s: %s ", self.proto.name, self.proto.to_string(self.frameID))
            logger.debug("Frame ID  mask by proto %s: %s ", self.proto.name, self.proto.to_string(self.frameID_mask))

        fid, ask = self.get_frameId()  # FOR DEBUG
        self._is_id_changing_ = False

    def clear_frameID(self):
        self.set_frameID(0, 0x1FFFFFFF)

    def get_frameId(self):
        f_bits = [0] * 29
        m_bits = [0] * 29

        idLen = int(29 if self.is_IDExt else 16)
        # logger.debug("idlen %s",idLen)
        for i in range(idLen):
            # logger.debug("Index = %s,  CheckBoxId = %s", idLen-i, i)
            f_bits[idLen-i-1] = str(self.__dict__[self.id_f_bits[i]].value())
            m_bits[idLen-i-1] = str(self.__dict__[self.id_m_bits[i]].value())

        # for i in range(0, idLen+1):
        logger.debug("id %s, mask %s",  "".join(f_bits[0:idLen]), "".join(m_bits[0:idLen] ))
        # logger.debug("mask %s", "".join(m_bits[0:idLen]))

        return int("".join(f_bits[0:idLen]), 2) & 0x1FFFFFFF, int("".join(m_bits[0:idLen]), 2) & 0x1FFFFFFF

    def _ch_frameId_hex_evt(self, name):
        # logger.debug("Got event")
        if name == "mask":
            value = self.frameidmask_hex_edit.text()
            self.frameID_mask = int(value, 16) & 0x1FFFFFFF
        else:
            value = self.frameid_hex_edit.text()
            # value = self.frameid_hex_edit.selectedText()
            self.frameID = int(value, 16) & 0x1FFFFFFF
        self.set_frameID(self.frameID, self.frameID_mask)
        fid, ask = self.get_frameId() # FOR DEBUG

    def _ch_frameId_evt(self, value_as_unicode):
        self.frameID, self.frameID_mask = self.get_frameId()
        logger.debug("Got event. Val = %s, id=0x%08X, mask=0x%08X", value_as_unicode, self.frameID, self.frameID_mask)
        self.set_frameID(self.frameID, self.frameID_mask)

    def get_type(self):
        if self.wait_rbtn.isChecked():
            return SMH.ACTION_WAIT
        else:
            return SMH.ACTION_SEND

    def set_type(self, type):
        if type == SMH.ACTION_WAIT:
            self.wait_rbtn.setChecked(True)
            self.send_rbtn.setChecked(False)
            self.action = SMH.ACTION_WAIT

        elif type == SMH.ACTION_SEND:
            self.wait_rbtn.setChecked(False)
            self.send_rbtn.setChecked(True)
            self.action = SMH.ACTION_SEND

    def set_data_len(self, length):
        logger.debug("Set data len %s.", str(length))
        if length > 8:
            return
        for x in range(0, length):
            for y in range(0, 8):
                self.__dict__[self.data_f_bits[x][y]].setDisabled(False)
                self.__dict__[self.data_m_bits[x][y]].setDisabled(False)

        for x in range(length, 8):
            for y in range(0, 8):
                self.__dict__[self.data_f_bits[x][y]].setDisabled(True)
                self.__dict__[self.data_m_bits[x][y]].setDisabled(True)

        self.dataLen = length
        self.data_len_spin.setValue(length)

    def _ch_data_byte_evt(self):
        if self._is_data_changing_:
            return
        self._is_data_changing_ = True
        n = list(self.parentWidget.sender().objectName())
        byte_num = int(n[2]) - 1
        if n[0] == "D":
            if n[1] == "B":  # Change data bit
                self.dataAr[byte_num] = self.get_data_byte(self.data_f_bits, byte_num)
                logger.debug("Change data byte, caller=%s, byte=%d, val=%02X",
                             self.parentWidget.sender().objectName(),
                             byte_num,
                             self.dataAr[byte_num]
                             )
                self.__dict__["BDH{:1d}".format(byte_num + 1)].setText("0x{:02X}".format(self.dataAr[byte_num]))

            elif n[1] == "F":  # Change filter bit
                self.dataAr_mask[byte_num] = self.get_data_byte(self.data_m_bits, byte_num)
                logger.debug("Change data mask byte, caller=%s, byte=%d, val=%02X",
                             self.parentWidget.sender().objectName(),
                             byte_num,
                             self.dataAr_mask[byte_num]
                             )
                self.__dict__["BDM{:1d}".format(byte_num + 1)].setText("0x{:02X}".format(self.dataAr_mask[byte_num]))

        self._is_data_changing_ = False

    def get_data_byte(self, bytes_ar: list, byte_num):
        bitAr = [0] * 8
        for i in range(0, 8):
            bitAr[7 - i] = str(self.__dict__[bytes_ar[byte_num][i]].value())
        return int("".join(bitAr), 2)

    def set_data_bytes(self, bytes_ar: list, mask_ar: list = None):
        # self._is_data_changing_ = True

        local_mask: bytearray = mask_ar
        if self.isMask and mask_ar is None:
            local_mask: bytearray = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        logger.debug("Set data {}, mask {}".format( " ".join(hex(n) for n in bytes_ar),
                                                       " ".join( hex(n) for n in local_mask)))

        for i in range(0, min(len(bytes_ar), self.dataLen)):
            # for i in range(0, len(bytes_ar)):
            # self._set_data_byte(i, bytes_ar[i])
            bitAr = list("{:08b}".format(bytes_ar[i]))
            for j in range(0, 8):
                self.__dict__[self.data_f_bits[i][j]].setValue(int(bitAr[7 - j]))

            if local_mask is not None:
                # self._set_dataMask_byte(i, local_mask[i])
                bitAr = list("{:08b}".format(local_mask[i]))
                for j in range(0, 8):
                    self.__dict__[self.data_m_bits[i][j]].setValue(int(bitAr[7 - j]))

        # self._is_data_changing_ = False

    # def _set_data_byte(self, index, byte):
    #     self.dataAr[index] = byte
    #     bitAr = list("{:08b}".format(byte))
    #     for i in range(0, 8):
    #         self.__dict__[self.data_f_bits[index][i]].setValue(int(bitAr[7-i]))
    #
    # def _set_dataMask_byte(self, index, byte):
    #     self.dataAr[index] = byte
    #     bitAr = list("{:08b}".format(byte))
    #     for i in range(0, 8):
    #         self.__dict__[self.data_m_bits[index][i]].setValue(int(bitAr[7-i]))
    #
