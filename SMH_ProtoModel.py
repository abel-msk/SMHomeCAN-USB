import logging
import os
import sys
import typing

from PyQt5.QtCore import Qt, QModelIndex, QVariant, QSize, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle, QHeaderView, QMessageBox, QWidget
from SMH_Proto import CustomProto, ProtoSlice

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class Communicate(QObject):
    error = pyqtSignal(str)
    changed = pyqtSignal(str, QModelIndex)


class SelectorDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices

    def paint(self,  painter: QtGui.QPainter, option, index: QtCore.QModelIndex):
        if isinstance(self.parent(), QtWidgets.QAbstractItemView):
            self.parent().openPersistentEditor(index)
        super(SelectorDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.currentIndexChanged.connect(self.commit_editor)
        editor.addItems(self.items)
        return editor

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        num = self.items.index(value)
        editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ButtonDelegate(QtWidgets.QStyledItemDelegate):

    clicked = QtCore.pyqtSignal(str, QtCore.QModelIndex)

    def __init__(self, owner, label=""):
        super().__init__(owner)
        self.label = label

    def paint(self, painter: QtGui.QPainter, option, index: QtCore.QModelIndex):
        # if isinstance(self.parent(), QtWidgets.QAbstractItemView):
        #     self.parent().openPersistentEditor(index)
        # super(ButtonDelegate, self).paint(painter, option, index)
        if (
            isinstance(self.parent(), QtWidgets.QAbstractItemView)
            and self.parent().model() is index.model()
        ):
            self.parent().openPersistentEditor(index)

    def createEditor(self, parent, option, index):

        frame = QtWidgets.QFrame(parent)
        frame.setObjectName("cell frame")

        cell_la = QtWidgets.QHBoxLayout(frame)
        cell_la.setContentsMargins(0, 0, 0, 0)
        cell_la.setObjectName("h_la")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        cell_la.addItem(spacerItem)

        btn = QtWidgets.QPushButton(frame)
        btn.setAutoDefault(False)
        btn.setObjectName("btn")
        btn.setText(self.label)
        btn.clicked.connect(lambda *args, ix=index: self.clicked.emit("up", ix))
        cell_la.addWidget(btn)
        return frame

    # def setEditorData(self, editor, index):
    #     pass
    #
    # def setModelData(self, editor, model, index):
    #     pass
    #
    # def updateEditorGeometry(self, editor, option, index):
    #     # editor.setGeometry(option.rect)
    #     pass


class ProtoTableModel(QtCore.QAbstractTableModel):
    """
    Represent headers parameters table

                            0            1             2             3            4          5
                        +-------------+-------------+-------------+-------------+----------+-------
    Rows[0] (Slice)     | Slice name  | Short name  | start       | len         | view_as  |  Actions
                        +-------------+-------------+-------------+-------------+----------+-------
    Rows[1] (Slice)     | Slice name  | Short name  | start       | len         | view_as  |  Actions
                        +-------------+-------------+-------------+-------------+----------+-------
                        |
                         ....
    """
    error = pyqtSignal(str)
    changed = pyqtSignal(str, QtCore.QModelIndex)

    def __init__(self, proto: CustomProto ):
        super(ProtoTableModel, self).__init__()
        self.comm = Communicate()
        self.proto: CustomProto = proto
        if self.proto is None:
            self.proto = CustomProto()

        self.parent = None
        self.headers = ["Slice Name", "Short", "Start", "Len", "View As", "Actions"]
        self.columns = ["name", "short", "start", "len", "view_as"]

    def data(self, index: QModelIndex, role: int = ...):
        if index.column() >= len(self.columns):
            return
        if role == Qt.UserRole:
            return self.proto.slices[index.row()]
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            sl: ProtoSlice = self.proto.slices[index.row()]
            return getattr(sl, self.columns[index.column()])
        elif role == Qt.TextAlignmentRole:
            value = getattr(self.proto.slices[index.row()], self.columns[index.column()])
            if isinstance(value, int):
                return Qt.AlignCenter

        # elif role == Qt.CheckStateRole:
        # elif role == Qt.SizeHintRole:
        # Qt.SizeHintRole QSize
        # Qt.TextAlignmentRole  Qt.Alignment

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...):
        try:
            if index.column() <= len(self.columns):
                if role == Qt.EditRole:
                    sl = self.proto.slices[index.row()]
                    setattr(sl, self.columns[index.column()], value)
                    logger.debug("Edit cell row=%s, column=%s value=%s", index.row(), index.column(), value)
                    self.comm.changed.emit("set", index)
            return super().setData(index, value, role)

        except KeyError as err:
            self.comm.error.emit(err)

    def flags(self, index):
        if index.column() > len(self.columns):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
            # return super().flags(index)
        else:
            return super().flags(index) | Qt.ItemIsEditable        # Return edit text

    def rowCount(self, parent: QModelIndex = ...):
        # The length of the outer list.
        return len(self.proto.slices)

    def columnCount(self, parent: QModelIndex = ...):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        # section is the index of the column/row.
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                tmp_val = self.headers[section]
                if tmp_val is None:
                    return ""
                return tmp_val
            # elif role == Qt.SizeHintRole:
            #     if section > 0 and (section < len(self.tbl_headers) - 1):
            #         w = self.parent.fontMetrics().horizontalAdvance(self.tbl_headers[section],
            #                                                            len(self.tbl_headers[section]))
            #         # logger.debug("Size request for column %s, width=%s", section, w)
            #         return QSize(w + 20, 0)

    def insertRow(self, row: int, parent: QModelIndex = ...):
        try:
            self.beginInsertRows(QModelIndex(), row+1, row+1)
            sl: ProtoSlice = self.proto.slices[row-1]
            logger.debug("Inserting after slice %s(%s), start=%s, new start = %s", sl.name, sl.short, sl.start, sl.start-sl.len )
            new_sl = self.proto.insert(name="tmp", start=sl.start-sl.len, len=1)
            self.endInsertRows()
            self.comm.changed.emit("ins", self.createIndex(self.proto.get_index(new_sl.short), 0))
            return True
        except KeyError as err:
            self.comm.error.emit(err)

    def removeRow(self, row: int, parent: QModelIndex = ...):
        try:
            self.beginRemoveRows(QModelIndex(), row, row)
            logger.debug("Removing slice %s(%s), start=%s", self.proto.slices[row].name, self.proto.slices[row].short, self.proto.slices[row].start)
            self.proto.delete(self.proto.slices[row].short)
            self.endRemoveRows()
            self.comm.changed.emit("rm", self.createIndex(row, 0))
            return True
        except KeyError as err:
            self.comm.error.emit(err)
