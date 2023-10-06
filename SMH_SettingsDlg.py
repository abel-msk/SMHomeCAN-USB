import sys
from PyQt5.QtCore import pyqtSignal, QObject
import logging
from logging import StreamHandler, Formatter
import copy

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QLineEdit, QPlainTextEdit

import SMH
from SMHomeSettings import Ui_SettingsDialog

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class Communicate(QObject):
    ok_signal = pyqtSignal(dict)


class SDialog(Ui_SettingsDialog):
    ok_signal = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(SDialog, self).__init__(*args, **kwargs)
        self.c = Communicate()
        self.parentWidget = None
        self.data: dict = {}

    def setupUi(self, dialog):
        self.parentWidget = dialog
        super(SDialog, self).setupUi(dialog)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)
        # self.cancel_btn.clicked.connect(lambda: self.close())
        self.FilterFGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_FILTERED_FG))
        self.FilterBGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_FILTERED_BG))
        self.RcvBGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_RCV_BG))
        self.RcvFGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_RCV_FG))
        self.SendBGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_SEND_BG))
        self.SendFGBtn.clicked.connect(lambda: self.select_color(SMH.ST_COLOR_SEND_FG))

    def set_data(self, data: dict):
        self.data = copy.deepcopy(data)
        self.display_color_test()

    def accept(self):
        logger.debug("OK btn clicked.")
        # data = copy.deepcopy(self.data)
        self.c.ok_signal.emit(self.data)
        self.parentWidget.close()

    def close(self):
        logger.debug("CLOSE btn clicked.")
        self.parentWidget.close()

    def select_color(self, ptr):
        color: QColor = QColorDialog.getColor()

        if color.isValid():
            logger.debug("Got color: %s", color.name())
            self.data[ptr] = color.name()

        self.display_color_test()

    def display_color_test(self):
        self.FilterTest.clear()
        self.FilterTest.appendHtml(
            '<span style="background-color:' + self.data[SMH.ST_COLOR_FILTERED_BG] +
            '; color:' + self.data[SMH.ST_COLOR_FILTERED_FG] + '">' +
            "quick brown fox jumps over the lazy dog" +
            "</span>"
        )
        self.RcvTest.appendHtml(
            '<span style="background-color:' + self.data[SMH.ST_COLOR_RCV_BG] +
            '; color:' + self.data[SMH.ST_COLOR_RCV_FG] + '">' +
            "quick brown fox jumps over the lazy dog" +
            "</span>"
        )
        self.SendTest.appendHtml(
            '<span style="background-color:' + self.data[SMH.ST_COLOR_SEND_BG] +
            '; color:' + self.data[SMH.ST_COLOR_SEND_FG] + '">' +
            "quick brown fox jumps over the lazy dog" +
            "</span>"
        )

