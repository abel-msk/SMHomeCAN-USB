import sys

from PyQt5.QtCore import pyqtSignal, QObject, QModelIndex, Qt
import logging
from logging import StreamHandler, Formatter
import copy

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QLineEdit, QPlainTextEdit, QMessageBox

import SMH
import SMH_Proto
from SMH_Proto import CustomProto
from SMH_ProtoModel import ProtoTableModel, SelectorDelegate, ButtonDelegate
from SMHomeProtoEdit import Ui_ProtocolEditDialog

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class Communicate(QObject):
    accept = pyqtSignal(CustomProto)


class ProtoEditDialog(Ui_ProtocolEditDialog):
    accept = pyqtSignal(CustomProto)

    def __init__(self, *args, **kwargs):
        super(ProtoEditDialog, self).__init__(*args, **kwargs)
        self.comm = Communicate()
        self.parentWidget = None
        self.id_proto_model: ProtoTableModel = None
        self.proto: CustomProto = CustomProto()

    def setupUi(self, dialog):
        self.parentWidget = dialog
        super(ProtoEditDialog, self).setupUi(dialog)
        self.cancel_btn.clicked.connect(self.close)
        self.save_btn.clicked.connect(self.save)
        self.parentWidget.resize(750, 550)

    def set_proto(self, proto: CustomProto):
        self.proto = proto.dub()
        self.id_proto_model = ProtoTableModel(self.proto)
        self.id_proto_model.comm.error.connect(self._on_model_error)
        self.id_proto_model.comm.changed.connect(self._on_model_changed)
        self.frameid_slices_tbl.setModel(self.id_proto_model)

        dsel = SelectorDelegate(self.frameid_slices_tbl, SMH_Proto.VIEW_TYPES)
        self.frameid_slices_tbl.setItemDelegateForColumn(4, dsel)

        dbtn = ButtonDelegate(self.frameid_slices_tbl, "Remove")
        self.frameid_slices_tbl.setItemDelegateForColumn(5, dbtn)
        dbtn.clicked.connect(self._on_remove_slice)

        self.proto_name.setText(proto.name)
        self.proto_name.setReadOnly(True)
        self.proto_descr.clear()
        self.proto_descr.appendPlainText(proto.descr)

        self.update_gap_selector()
        self.add_slice_btn.clicked.connect(self._on_add_slice)

    def _on_remove_slice(self, lbl, ix: QModelIndex):
        logger.debug("Remove btn clicked on row=%s", ix.row())
        self.id_proto_model.removeRow(ix.row(), ix)

    def _on_add_slice(self):
        obj = self.gap_selector.currentData(role=Qt.UserRole)
        if obj is not None:
            logger.debug("Add slice btn clicked for gap start =%s", obj["start"])
            index = self.proto.get_index(obj["after"])
            self.id_proto_model.insertRow(index)

    def _on_model_error(self, err_str):
        msgBox = QMessageBox(self.parentWidget)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(err_str)
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok)
        # msgBox.buttonClicked.connect(msgButtonClick)
        returnValue = msgBox.exec()

    def _on_model_changed(self, act: str, index: QModelIndex):
        self.update_gap_selector()

    def update_gap_selector(self):
        ind = 0
        self.gap_selector.clear()
        for gap in self.proto.get_gaps():
            self.gap_selector.addItem("Start bit:{}, len:{}".format(gap["start"], gap["len"]), gap)
            logger.debug("Found slice gap at start %s", gap["start"])
            ind += 1

    def close(self):
        logger.debug("OK btn clicked.")
        # data = copy.deepcopy(self.data)
        self.parentWidget.close()

    def save(self):
        self.comm.accept.emit(self.proto)
        self.parentWidget.close()


