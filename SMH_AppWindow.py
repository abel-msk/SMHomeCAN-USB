import copy
import os
import sys
import logging
import calendar
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QThreadPool, QWaitCondition, QMutex
from PyQt5.QtGui import QColor, QPalette, QFont

import SMH
import SMH_Proto
from CAN_Packet import CANPacket
from SMH_FilterEditDlg import FilterEditDialog
import SMH_CANWorker
from SMH_CANWorker import CANWorker
from SMH_FilterTree import FilterTree, FilterElement
from SMH_Proto import CustomProto
from SMH_ProtoEditDlg import ProtoEditDialog
from SMH_SettingsDlg import SDialog
from SMHomeMain import Ui_MainWindow
from logging import StreamHandler, Formatter
from PyQt5.QtWidgets import *

from config import Config

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(module)s-%(funcName)s: %(message)s'))
handler.setFormatter(Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))

logger.addHandler(handler)

# Info dialogs types
DLG_QUESTION = 1
DLG_ERROR = 2
DLG_WARNING = 3
DLG_INFO = 4

#  Rounded corner
# label.setStyleSheet(" \
#   border-image: url('demo.jpg'); \
#   background-color: black; \
#   border-radius: 50%; \
#   ")

#  Connection statuses constants
STATUS_NOT_CONNECTED = 1
STATUS_CONNECTED = 2
STATUS_WORK = 3


class AppWindow(QMainWindow, Ui_MainWindow):

    LAST_FRULE_FILE = "current_frule_path"
    _translate = QtCore.QCoreApplication.translate
    LAST_PROTO_FILE = "current_proto_path"
    DISPLAY_WITH_PROTO = "display_with_proto"

    def __init__(self, *args, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)
        self._translate = QtCore.QCoreApplication.translate

        self.config: Config = None
        self.setupUi(self)
        self.setObjectName("MAC UPB-CAN")
        self.setWindowTitle("MAC USB-CAN")

        self.capture_count = 0
        self.filtered_count = 0
        #static PySide2.QtGui.QColor.fromRgb(rgb)
        #static PySide2.QtGui.QColor.fromRgb(r, g, b[, a=255])
        cur_palete = self.PktTrace.palette()
        self.default_fg = cur_palete.color(QPalette.Text).name()
        self.default_bg = cur_palete.color(QPalette.Base).name()

        font = QFont()
        font.setFamily("Courier New")
        font.setPointSize(12)
        font.setUnderline(False)
        font.setKerning(False)
        self.PktTrace.setFont(font)

        self.color_setting = {
            SMH.ST_COLOR_FILTERED_FG: self.default_fg,
            SMH.ST_COLOR_FILTERED_BG: self.default_bg,
            SMH.ST_COLOR_SEND_FG: self.default_fg,
            SMH.ST_COLOR_SEND_BG: self.default_bg,
            SMH.ST_COLOR_RCV_FG: self.default_fg,
            SMH.ST_COLOR_RCV_BG: self.default_bg,
            SMH.ST_FONT_CAPT: "Courier New",
            SMH.ST_FONT_CAPT_SIZE: 12
        }

        bar = self.menuBar()
        bar.setNativeMenuBar(True)

        # FILTER  menu

        fRules = bar.addMenu("Filter")

        fRules_open = QAction("Open", self)
        fRules_open.setStatusTip("&Open an existing rules")
        fRules_open.setShortcut("Ctrl+O")
        fRules_open.triggered.connect(self.on_filter_file_open)
        fRules.addAction(fRules_open)

        fRules_save = QAction("&Save", self)
        fRules_save.setStatusTip("Save rules")
        fRules_save.setShortcut("Ctrl+S")
        fRules_save.triggered.connect(self.on_filter_file_save)
        fRules.addAction(fRules_save)

        fRules_save_as = QAction("Save As ...", self)
        fRules_save_as.setStatusTip("Save rules in new file")
        fRules_save_as.triggered.connect(self.on_filter_file_save_as)
        fRules.addAction(fRules_save_as)

        fRules.addSeparator()

        fRules_quit = QAction("&Quit", self)
        fRules_quit.setStatusTip("Close application")
        fRules_quit.triggered.connect(self.close)
        fRules.addAction(fRules_quit)

        # PROTOCOL  menu
        proto_menu = bar.addMenu("Protocol")

        proto_load = QAction("Load", self)
        proto_load.triggered.connect(self.on_proto_file_open)
        proto_load.setStatusTip("Load protocol description from file")
        proto_menu.addAction(proto_load)

        proto_def = QAction("Set default", self)
        # fRules_st.triggered.connect(self.on_settings_edit)
        proto_def.setStatusTip("Set current protol mask to load at startup.")
        proto_menu.addAction(proto_def)

        proto_edit = QAction("New/Edit", self)
        proto_edit.triggered.connect(self.on_proto_edit)
        proto_edit.setStatusTip("Modify or create new protocol masks definition.")
        proto_menu.addAction(proto_edit)

        proto_edit = QAction("Save", self)
        proto_edit.triggered.connect(self.on_proto_file_save)
        proto_edit.setStatusTip("Modify or create new protocol masks definition.")
        proto_menu.addAction(proto_edit)

        proto_edit = QAction("Save As", self)
        proto_edit.triggered.connect(self.on_proto_file_save_as)
        proto_edit.setStatusTip("Modify or create new protocol masks definition.")
        proto_menu.addAction(proto_edit)

        # SETTINGS menu
        settings = bar.addMenu("Settings")
        fRules_st = QAction("Property", self)
        fRules_st.triggered.connect(self.on_settings_edit)
        fRules_st.setStatusTip("Interface settings")
        settings.addAction(fRules_st)

        # TODO: Add Quit menu

        # self.threadpool = QThreadPool()
        self.cond = QWaitCondition()
        self.lock = QMutex()

        self.CANThread = CANWorker(self.cond, self.lock)
        self.CANThread.signals.error.connect(self.on_thread_error)
        self.CANThread.signals.display.connect(self.on_display_pkt)

        # QThreadPool.globalInstance().start(self.CANThread)
        self.threadpool = QThreadPool()
        self.threadpool.start(self.CANThread)

        self.AddFRuleBtn.clicked.connect(self.on_filter_add_open)
        self.DelFRuleBtn.clicked.connect(self.on_filter_delete)
        self.ConnBtn.clicked.connect(self.on_connect)
        self.StartBtn.clicked.connect(self.on_capture_start)
        self.StopBtn.clicked.connect(self.on_capture_stop)
        self.StopCaptBtn.clicked.connect(self.on_capture_stop)
        self.CaptBtn.clicked.connect(self.on_capture_all)
        self.SaveBtn.clicked.connect(self.on_capture_save)
        self.RulesTree.doubleClicked.connect(self.on_filter_edit_open)
        self.use_proto_chk.stateChanged.connect(self.on_filter_view_changed)

        self.proto: CustomProto = None
        self.is_proto = False
        self.proto_filename = ""

        self.FTree: FilterTree = FilterTree(self.RulesTree)
        self.FTree.use_proto = False
        self.filter_filename = None

        self.connect_status = STATUS_NOT_CONNECTED
        self.set_status(STATUS_NOT_CONNECTED)
        self.show()

    def setup(self, conf: Config):
        self.config = conf
        for key in self.color_setting.keys():
            val = self.config.get_value(key)
            if val is not None:
                self.color_setting[key] = val
        self.apply_settings(self.color_setting)

        if self.config and self.config.has_value(AppWindow.DISPLAY_WITH_PROTO):
            display_proto = self.config.get_value(AppWindow.LAST_PROTO_FILE)
            if display_proto:
                self.use_proto_chk.setChecked(True)
            else:
                self.use_proto_chk.setChecked(False)

        if self.config and self.config.has_value(AppWindow.LAST_PROTO_FILE):
            logger.debug("load config file %s", self.config.get_value(AppWindow.LAST_PROTO_FILE))
            self.proto_filename = self.config.get_value(AppWindow.LAST_PROTO_FILE)
            self.proto = SMH_Proto.proto_file_load(self.proto_filename)
            self.is_proto = True

            self.FTree.set_proto(self.proto)
            if self.use_proto_chk.isChecked():
                self.FTree.use_proto = True
            else:
                self.FTree.use_proto = False

        if self.config and self.config.has_value(AppWindow.LAST_FRULE_FILE):
            logger.debug("load config file %s", self.config.get_value(AppWindow.LAST_FRULE_FILE))
            self.filter_filename = self.config .get_value(AppWindow.LAST_FRULE_FILE)
            self.FTree.load_json_file(self.filter_filename)

    def apply_settings(self, new_set: dict):
        self.color_setting = new_set
        font = QFont()
        font.setFamily(self.color_setting[SMH.ST_FONT_CAPT])
        font.setPointSize(self.color_setting[SMH.ST_FONT_CAPT_SIZE])
        font.setUnderline(False)
        font.setKerning(False)
        self.PktTrace.setFont(font)

    def on_connect(self):
        # with QtCore.QMutexLocker(self.lock):
        if self.CANThread.is_connected():
            self.CANThread.set_CMD(SMH_CANWorker.CMD_RESET)
            # self.ConnBtn.setText(self._translate("MainWindow", "Connect"))
            with QtCore.QMutexLocker(self.lock):
                self.cond.wait(self.lock)
                bus, addr, sn, info = self.CANThread.get_devinfo()
                self.show_conn_info(bus, addr, sn, info)
                logger.debug("Reset. Is connected=%s", self.CANThread.is_connected())
        else:
            self.CANThread.set_CMD(SMH_CANWorker.CMD_CONNECT)
            with QtCore.QMutexLocker(self.lock):
                self.cond.wait(self.lock)
                if self.CANThread.is_connected():
                    bus, addr, sn, info = self.CANThread.get_devinfo()
                    self.show_conn_info(bus, addr, sn, info)

                    # Change name of the connect button
                    self.ConnBtn.setText(self._translate("MainWindow", "Reset"))

    def set_status(self, new_status):
        if new_status == STATUS_NOT_CONNECTED:
            self.StatusTxt.setText("Not Connected")
            self.StatusTxt.setStyleSheet("background-color: rgb(210,210,210);  border-radius: 5; padding: 2")
        elif new_status == STATUS_CONNECTED:
            self.StatusTxt.setText("Connected")
            self.StatusTxt.setStyleSheet("background-color: rgb(254,203, 47); border-radius: 5; padding: 2")
        elif new_status == STATUS_WORK:
            self.StatusTxt.setText("Running")
            self.StatusTxt.setStyleSheet("background-color: rgb(79, 226, 97);  border-radius: 5; padding: 2")
        self.connect_status = new_status

    def set_status_down(self):
        if self.connect_status == STATUS_CONNECTED:
            self.set_status(STATUS_NOT_CONNECTED)
        elif self.connect_status == STATUS_WORK:
            self.set_status(STATUS_CONNECTED)

    def on_thread_error(self, msg):
        logger.debug("Connect error: %s", msg)
        self.show_dialog(DLG_ERROR, msg)
        self.set_status_down()

    def on_filter_view_changed(self, check):
        logger.debug("Filter view changed %s", check)
        self.FTree.use_proto = True if check > 0 else False
        self.RulesTree.clear()
        self.FTree.display_tree()

    def on_filter_file_open(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            os.getenv('HOME'), "All files (*)")

        logger.debug("Open File. %s", fname[0])
        if fname[0] != "":
            # Load rule file
            self.filter_filename = fname[0]
            self.FTree.load_json_file(self.filter_filename)
            self.config.set_value(self.LAST_FRULE_FILE, self.filter_filename)

    def on_filter_file_save(self):
        logger.debug("Save file. Name=%s", self.filter_filename)
        if self.filter_filename is not None:
            self.FTree.save_json_file(self.filter_filename)
        else:
            self.on_filter_file_save_as()

    def on_filter_file_save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Save File')

        logger.debug("Open File. %s", fname[0])
        if fname[0] != "":
            self.FTree.save_json_file(fname[0])
            self.filter_filename = fname[0]

    def on_settings_edit(self):
        logger.debug("Open settings dialog")
        dialog_window = QtWidgets.QDialog()
        st_dialog = SDialog()
        st_dialog.setupUi(dialog_window)
        st_dialog.set_data(self.color_setting)
        st_dialog.c.ok_signal.connect(self.on_settings_changed)
        dialog_window.setWindowModality(Qt.ApplicationModal)
        dialog_window.exec_()

    def on_settings_changed(self, data):
        logger.debug("Setting was changed.")
        self.color_setting = data

    def on_filter_add_open(self):
        dialog_window = QtWidgets.QDialog()
        add_dialog = FilterEditDialog()
        add_dialog.setupUi(dialog_window)
        if self.is_proto:
            add_dialog.setup_proto_UI(self.proto)

        if len(self.RulesTree.selectedItems()) > 0:
            curSelection = self.RulesTree.selectedItems()[0]
            cur_el: FilterElement = curSelection.data(0, Qt.UserRole)
            add_dialog.set_parentRuleID(cur_el.ruleId)

        add_dialog.comm.ok_signal.connect(self.on_filter_add)
        add_dialog.set_ruleID(self.FTree.increase_RuleID())

        dialog_window.setWindowModality(Qt.ApplicationModal)
        # dialog_window.show()
        dialog_window.exec_()

    def on_filter_add(self, data: dict):
        insert_after_id = -1
        # Get currently selected element
        if len(self.RulesTree.selectedItems()) > 0:
            curSelection = self.RulesTree.selectedItems()[0]
            cur_el: FilterElement = curSelection.data(0, Qt.UserRole)
            insert_after_id = cur_el.ruleId
        el = self.FTree.el_create(data, insert_after_id)
        self.FTree.item_insert(el)

    def on_filter_edit_open(self, index):
        item = self.RulesTree.selectedIndexes()[0]
        el: FilterElement = item.data(Qt.UserRole)
        logger.debug("Double clicked : %s", el.name)
        dialog_window = QtWidgets.QDialog()
        add_dialog = FilterEditDialog()
        add_dialog.setupUi(dialog_window)
        add_dialog.setupData(el.toDict())

        if self.is_proto:
            add_dialog.setup_proto_UI(self.proto)

        add_dialog.comm.ok_signal.connect(self.on_filter_edit)
        # add_dialog.c.ok_signal.connect(self.on_filter_changed)
        dialog_window.setWindowModality(Qt.ApplicationModal)
        # dialog_window.show()
        dialog_window.exec_()

    def on_filter_edit(self, data: dict):
        el: FilterElement = self.FTree.find_by_id(data[SMH.FL_ID])
        # ItemWidget = self.RulesTree.itemWidget(el.view_link, 0)
        item = el.view_link
        # self.RulesTree.model().layoutAboutToBeChanged.emit()
        if el.parent.ruleId != data[SMH.FL_PARENT_ID]:
            logger.info("Element %s, has changed parent. Move to parent %s", el.name, el.parent.name)
            # TODO:  Move element to other location in tree
        else:
            el.fromDict(data)
            logger.info("Element %s, has changed.", el.name)

        self.FTree.item_remove(item)
        self.FTree.item_insert(el)
        if el.has_child():
            for child_el in el.get_children():
                self.FTree.item_insert(child_el)

    def on_filter_delete(self):
        if len(self.RulesTree.selectedItems()) == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Select rule for delete")
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(QMessageBox.Ok)
            # msgBox.buttonClicked.connect(msgButtonClick)
            returnValue = msgBox.exec()
            return
        curSelection = self.RulesTree.selectedItems()[0]
        cur_el: FilterElement = curSelection.data(0, Qt.UserRole)

        returnValue = self.show_dialog(DLG_QUESTION, "Are You sure want to delete rule '{}' ?".format(cur_el.name))

        if returnValue == QMessageBox.Yes:
            self.FTree.el_remove(cur_el)
            self.FTree.item_remove(cur_el.view_link)

        logger.debug("Delete filter rule line {}".format(cur_el.name))

    def on_filter_changed(self, index):
        item = self.RulesTree.selectedIndexes()[0]
        logger.debug("Double clicked : %s", item.data(Qt.UserRole).name)

    def on_proto_edit(self):
        logger.debug("on_proto_edit event.  Open ProtoEditDialog")
        dialog_window2 = QtWidgets.QDialog()
        proto_dialog = ProtoEditDialog()
        proto_dialog.setupUi(dialog_window2)
        proto_dialog.set_proto(self.proto)
        proto_dialog.comm.accept.connect(self.on_proto_save)

        dialog_window2.setWindowModality(Qt.ApplicationModal)
        # dialog_window.show()
        dialog_window2.exec_()

    def on_proto_save(self, new_proto: CustomProto):
        self.proto = new_proto
        self.FTree.use_proto = True
        self.FTree.proto = self.proto

        # Redraw table
        self.RulesTree.clear()
        self.FTree.display_tree()

    def on_proto_file_open(self):
        fname = QFileDialog.getOpenFileName(self, 'Open proto mask file',
                                            os.getenv('HOME'), "All files (*)")
        if fname[0]:
            self.proto = SMH_Proto.proto_file_load(fname[0])
            self.proto_filename = fname[0]
            self.is_proto = True

            self.FTree.set_proto(self.proto)
            self.RulesTree.clear()
            self.FTree.display_tree()
            self.config.set_value(self.LAST_PROTO_FILE, self.proto_filename)

    def on_proto_file_save(self):
        if self.is_proto and self.proto_filename:
            SMH_Proto.proto_save(self.proto, self.proto_filename)

    def on_proto_file_save_as(self):
        if self.is_proto:
            fname = QFileDialog.getSaveFileName(self, 'Save File As')
            if fname[0] != "":
                logger.debug("Save protocol %s in file %s", self.proto.name, fname[0])
                self.proto_filename = fname[0]
                SMH_Proto.proto_save(self.proto, self.proto_filename)
                # self.proto.toJson()
                # self.proto_filename = fname[0]
        else:
            self.show_dialog(DLG_ERROR, "Not protocol mask loaded.")

    def closeEvent(self, event):
        """
        Event handler. Close main window
        :param event:
        :return:
        """
        # reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
        #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #
        # if reply == QMessageBox.Yes:
        #     event.accept()
        #     print('Window closed')
        # else:
        #     event.ignore()
        if self.CANThread.is_working:
            logger.debug("Detect working process.")
            self.CANThread.set_CMD(SMH_CANWorker.CMD_ABORT)
            with QtCore.QMutexLocker(self.lock):
                self.cond.wait(self.lock)
        logger.debug("Closing window.")
        self.CANThread.set_CMD(SMH_CANWorker.CMD_EXIT)
        with QtCore.QMutexLocker(self.lock):
            self.cond.wait(self.lock)
        if self.config is not None:
            self.save_config()

    def on_capture_save(self):
        fname = QFileDialog.getSaveFileName(self, 'Save File')
        if fname[0] != "":
            f = open(fname[0], "w")
            f.write(self.PktTrace.toPlainText())
            f.close()

    def save_config(self):
        """
        Save current configuration
        :return:
        """
        logger.debug("Save config to file %s",self.config.filename)
        self.config.set_value("width", super(AppWindow, self).width(), "window")
        self.config.set_value("height", super(AppWindow, self).height(), "window")

        # (x, y) = self.location_on_the_screen()
        self.config.set_value("x", self.pos().x(), "window")
        self.config.set_value("y", self.pos().y(), "window")

        for key in self.color_setting.keys():
            self.config.set_value(key, self.color_setting[key])

        if self.use_proto_chk.isChecked():
            self.config.set_value(AppWindow.DISPLAY_WITH_PROTO, True)
        else:
            self.config.set_value(AppWindow.DISPLAY_WITH_PROTO, False)

        self.config.save()

    def show_conn_info(self, bus, addr, sn, info):
        if sn:
            self.set_status(STATUS_CONNECTED)
        else:
            self.set_status(STATUS_NOT_CONNECTED)
        self.BusTxt.setText("0x{:04X}".format(bus))
        self.AddrTxt.setText("0x{:04X}".format(addr))
        self.SerNumTxt.setText(str(sn))
        self.InfoTxt.setText(info)

    def on_capture_start(self):
        if self.RulesTree.selectedIndexes():
            self.capture_count = 0
            self.filtered_count = 0
            item = self.RulesTree.selectedIndexes()[0]
            el: FilterElement = item.data(Qt.UserRole)
            self.CANThread.filters_list = [el]

            if self.RptSelBtn.isChecked():
                self.CANThread.is_repeat = True
            else:
                self.CANThread.is_repeat = False
            #  is repeated action
            if self.RptSelBtn.isChecked():
                self.CANThread.time_interval = int(self.TimeInterval.text()) if self.TimeInterval.text() else 0
            logger.info("Send capture START command to worker.")
            self.CANThread.set_CMD(SMH_CANWorker.CMD_START)
            self.set_status(STATUS_WORK)
        else:
            returnValue = self.show_dialog(DLG_ERROR, "Select fiter rules first.")

    def on_capture_stop(self):
        logger.info("Send capture STOP command to worker.")
        self.CANThread.set_CMD(SMH_CANWorker.CMD_STOP)
        with QtCore.QMutexLocker(self.lock):
            self.cond.wait(self.lock)
        self.set_status(STATUS_CONNECTED)

    def on_capture_all(self):
        self.capture_count = 0
        self.filtered_count = 0
        logger.info("Send CAPTURE ALL command to worker.")
        self.CANThread.set_CMD(SMH_CANWorker.CMD_CAPTURE)
        self.set_status(STATUS_WORK)

    def on_display_pkt(self, TS: float, filter_name, direction, pkt: CANPacket):
        """
        Receive event when worker send or receive CAN packet
        :param TS: timestamp
        :param filter_name: = packet was matched if sendet by this filter line object
        :param direction: 0 - Send; 1- Receice
        :param pkt: the CAN packet
        :return:
        """

        logger.debug("Got event send/receive filtered packet. Filter=%s %s", filter_name, direction)
        text_bg = self.default_bg
        text_fg = self.default_fg

        if not filter_name:
            text_bg = self.color_setting[SMH.ST_COLOR_FILTERED_BG]
            text_fg = self.color_setting[SMH.ST_COLOR_FILTERED_FG]
        elif direction == SMH_CANWorker.PKT_SEND:
            text_bg = self.color_setting[SMH.ST_COLOR_SEND_BG]
            text_fg = self.color_setting[SMH.ST_COLOR_SEND_FG]
        elif direction == SMH_CANWorker.PKT_RECEIVE:
            text_bg = self.color_setting[SMH.ST_COLOR_RCV_BG]
            text_fg = self.color_setting[SMH.ST_COLOR_RCV_FG]

        text_color = "darkgrey"
        # "float: left; width: 20px;"
        # display: inline-block; width: 200px;

        buff = "{:>10} {} | ".format(filter_name, "S" if direction == SMH_CANWorker.PKT_SEND else "R")
        buff = buff.replace(' ', '&nbsp;')

        packet_view = ""
        if self.use_proto_chk.isChecked():
            packet_view = self.proto.to_string(pkt.frameID) + " | " + pkt.data_hex()
        else:
            packet_view = pkt.id_bin() + " | " + pkt.data_hex()

        self.PktTrace.appendHtml('<span">{:.7f} '.format(TS) + buff + '</span>' +
                                 '<span style="background-color:' + text_bg + '">' +
                                 packet_view.replace(' ', '&nbsp;') +
                                 '</span>')

        self.capture_count += 1
        self.TotPktLbl.setText(str(self.capture_count))
        if not filter_name.strip():
            self.filtered_count += 1
            self.FltPktLbl.setText(str(self.filtered_count))

    def show_dialog(self, dlg_type, message):
        dlg = QMessageBox(self)
        dlg.setStandardButtons(QMessageBox.Ok)

        if dlg_type == DLG_ERROR:
            dlg.setWindowTitle("Critical")
            dlg.setIcon(QMessageBox.Critical)
        elif dlg_type == DLG_WARNING:
            dlg.setWindowTitle("Warning")
            dlg.setIcon(QMessageBox.Warning)
        elif dlg_type == DLG_INFO:
            dlg.setWindowTitle("Information")
            dlg.setIcon(QMessageBox.Information)
        elif dlg_type == DLG_QUESTION:
            dlg.setWindowTitle("")
            dlg.setIcon(QMessageBox.Question)
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        else:
            dlg.setIcon(QMessageBox.NoIcon)

        dlg.setText(message)

        returnValue = dlg.exec()
        return returnValue