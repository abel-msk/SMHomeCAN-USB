import copy
import queue
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject, QMutex, QWaitCondition
from CAN_USB_Drv import CANLibDrv, ConnectError
from CAN_Packet import CANPacket
import logging
import sys
import SMH
from CAN_USB_Receiver import CANReceiver
from SMH_FilterTree import FilterElement

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)

CMD_NONE = 0
CMD_CONNECT = 1
CMD_RESET = 2
CMD_START = 3
CMD_STOP = 6
CMD_EXIT = 4
CMD_CAPTURE = 5
CMD_ABORT = 7
CMD_TEST = 8

PKT_SEND = 0
PKT_RECEIVE = 1

from gs_usb.constants import (
    CAN_RTR_FLAG,
    CAN_EFF_FLAG
)


class Aborting(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        super().__init__("Aborting by user")


class CANSignals(QObject):
    display = pyqtSignal(float, str, int, CANPacket)
    error = pyqtSignal(str)


class CANWorker(QRunnable):
    """
    Can interface buffer exchange thread
    """

    def __init__(self, cond: QWaitCondition, lock: QMutex, *args, **kwargs):
        super(CANWorker, self).__init__()

        self.cond = cond
        self.lock = lock
        # self.lock = QtCore.QMutex()

        self.drv = CANLibDrv()
        self.bitrate = 500000
        self.deviceInfo = None
        self.cmd = 0
        self.signals = CANSignals()
        self.is_working = False

        self.is_display_all = False
        # self.is_connected = False
        # self.fiter_root: FilterElement = None
        self.filters_list: list = []
        self.time_interval = 0
        self.is_repeat = False
        self.test_count = 0
        self.deviceName = ""

    def set_display_all(self, is_display):
        with QtCore.QMutexLocker(self.lock):
            self.is_display_all = is_display
            
    def set_CMD(self, cmd):
        with QtCore.QMutexLocker(self.lock):
            self.cmd = cmd

    def get_CMD(self):
        with QtCore.QMutexLocker(self.lock):
            # logger.debug("Check CMD. Got %d",self.cmd)
            cmd = self.cmd
            self.cmd = CMD_NONE
            return cmd

    def set_bitrate(self, bitrate):
        with QtCore.QMutexLocker(self.lock):
            self.bitrate = bitrate

    def get_devinfo(self):
        return self.deviceInfo["bus"], self.deviceInfo["addr"], self.deviceInfo["sn"], self.drv.dev.gs_usb.product

    def is_connected(self):
        try:
            status = self.drv.status()
        except Exception as err:
            logger.error("ERROR %s", str(err), exc_info=True)
            status = False

        return status

    def _start(self):
        if not self.drv.status() or not self.drv.is_started:
            self.drv.start()

    def _stop(self):
        self.drv.stop()
        pass


    @pyqtSlot()
    def run(self) -> None:
        logger.debug("Thread run ...")
        while True:
            # with QtCore.QMutexLocker(self.lock):
            try:
                cmd = self.get_CMD()

                # DISCONNECT
                if self.is_connected() and cmd == CMD_RESET:
                    logger.debug("CMD RESET")
                    # for cns in range(0, 4):
                    #     self.drv.stop()
                    #     time.sleep(0.1)
                    #     self.drv.connect()
                    self.drv.stop()
                    if self.drv.dev is None:
                        self.drv.connect()
                    else:
                        self.drv.connect(self.drv.dev)

                # CONNECT
                if not self.is_connected() and cmd == CMD_CONNECT:
                    logger.debug("CMD CONNECT")
                    # if self.drv.dev is None:
                    self.drv.connect()
                    # else:
                    #     self._start()
                    self.deviceInfo = self.drv.get_info()
                    self.deviceName = self.drv.dev.gs_usb.product
                    if self.deviceInfo["sn"]:
                        logger.debug("Connected. dev=%s, S/N=%s", self.deviceInfo["info"], self.deviceInfo["sn"])

                # START CAPTURE
                elif cmd == CMD_START:
                    logger.debug("CMD START")
                    if self.drv.status():
                        self.is_working = True
                        if len(self.filters_list) > 0:
                            self.repeated_execution(self.filters_list, self.time_interval, self.is_repeat)
                        else:
                            self.signals.error.emit("Filter list does not selected.")
                        self.filters_list = []
                        self.is_working = False
                    else:
                        self.signals.error.emit("CAN_USB adapter does not connected.")

                # EXIT stop thread
                elif cmd == CMD_STOP:
                    logger.debug("CMD Stop")
                    self.is_working = False

                    # EXIT stop thread
                elif cmd == CMD_EXIT:
                    # self.cmd = CMD_NONE
                    logger.debug("CMD Exit")
                    self.cond.wakeAll()
                    return

                # CAPTURE ALL
                elif cmd == CMD_CAPTURE:
                    # self.cmd = CMD_NONE
                    logger.debug("CMD CAPTURE")
                    if self.drv.status():
                        self.is_working = True
                        self.capture_all()
                        self.is_working = False
                    else:
                        self.signals.error.emit("CAN_USB adapter does not connected.")

                #  TESTING
                elif cmd == CMD_TEST:
                    logger.debug("CMD TEST")
                    self.test_count = 0
                    self.is_working = True
                    self.capture_test()
                    self.is_working = False

            except ConnectError as err:
                logger.error("ERROR (ConnectError) %s", str(err))
                self.signals.error.emit(str(err))
            except Aborting as err:
                logger.debug(str(err))
                self._stop()
            except Exception as err:
                logger.error("ERROR %s", str(err), exc_info=True)
                self.signals.error.emit(str(err))
            finally:
                self.is_working = False

            self.cond.wakeAll()
            time.sleep(0.1)

    def capture_all(self):
        self._start()  # Start USB
        self.drv.read_start()
        try:
            while True:
                pkt: CANPacket = self.read_packet()
                self.signals.display.emit(time.time(), " ", PKT_RECEIVE, pkt)
                if self.is_abort():
                    raise Aborting

        except Exception as err:
            raise err
        finally:
            self.drv.read_stop()
            self._stop()

    def capture_test(self):
        """
        Tesing receive signal.  Emit receice signal w/o  real receive any packet&
        :return:
        """
        while True:
            self.test_count += 1
            pkt: CANPacket = CANPacket()

            a, c = divmod(self.test_count, 2)
            pkt.dataLen = 2 if c == 0 else 8
            pkt.dataAr = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
            pkt.frameID = self.test_count

            self.signals.display.emit(time.time(), " ", PKT_RECEIVE, pkt)
            time.sleep(0.001)
            if self.is_abort():
                raise Aborting

    def repeated_execution(self, filter_list: list, timeout: int = 0, repeat=False):
        self._start()
        self.drv.read_start()
        try:
            while True:
                if filter_list[0].action == SMH.ACTION_WAIT:
                    self.wait_and_send(filter_list)
                else:
                    self.send_and_wait(filter_list)

                if self.is_abort():
                    raise Aborting
                if not repeat:
                    self.drv.read_stop()
                    return

                if timeout > 0:
                    time.sleep(timeout)

        except Exception as err:
            # logger.debug("Receive Exception:  %s", err)
            self.drv.read_stop()
            self._stop()
            raise err

    def wait_and_send(self, filter_list):
        is_match = False
        while not is_match:
            if self.is_abort():
                raise Aborting
            pkt: CANPacket = self.read_packet()
            for filter_el in filter_list:
                if self.match_packet(filter_el, pkt):
                    is_match = True
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("PKT MATCH \t %s", pkt)
                    self.signals.display.emit(time.time(), filter_el.name, PKT_RECEIVE, pkt)
                    if filter_el.has_child():
                        self.send_and_wait(filter_el.has_child)
                    break
                elif self.is_display_all:
                    self.signals.display.emit(time.time(), " ", PKT_RECEIVE, pkt)

    def send_and_wait(self, filter_list):
        for filter_el in filter_list:
            if filter_el.action == SMH.ACTION_SEND:
                self.send_packet(filter_el.base)
                self.signals.display.emit(time.time(), " ", PKT_SEND, filter_el.base)
                if filter_el.has_child():
                    self.wait_and_send(filter_el.child)
            if self.is_abort():
                raise Aborting

    def is_abort(self) -> bool:
        with QtCore.QMutexLocker(self.lock):
            if self.cmd == CMD_ABORT or self.cmd == CMD_STOP:
                self.cmd = CMD_NONE
                logger.debug("Got Abort CMD")
                self.filters_list = []
                # if self.drv.status():
                    # self.drv.stop()  ### TODO: have problems
                self.is_working = False
                return True
        return False

    def read_packet(self) -> CANPacket:
        receive = False
        pkt = None
        while not receive:
            frame = self.drv.rcv(tout=1)  # timeout in secs
            if frame is not None:
                pkt = CANPacket()
                pkt.dataFrame = frame[SMH.FR_DATA]
                pkt.extFrame = frame[SMH.FR_ID_EXT]
                pkt.frameID = frame[SMH.FR_ID]
                pkt.dataLen = frame[SMH.FR_DATA_LEN]
                pkt.dataAr = copy.copy(frame[SMH.FR_DATA_AR])

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("PKT RECEIVE \t %s", pkt)
                receive = True

            if self.is_abort():
                raise Aborting

        return pkt

    def send_packet(self, pkt: CANPacket):
        self.drv.send(canid=pkt.frameID,
                       data_len=pkt.dataLen,
                       data=pkt.dataAr,
                       canflag=CAN_EFF_FLAG if pkt.extFrame else 0
                       )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("PKT SEND %s", pkt)
        return True

    def match_packet(self, filter_el: FilterElement, pkt: CANPacket) -> bool:
        if filter_el.mask_empty:
            if filter_el.base.frameID != pkt.frameID:
                return False
            if filter_el.base.dataLen == 0:
                return True
            # Compare data array byte by byte w/o mask
            for i in range(0, filter_el.base.dataLen):
                if filter_el.base.dataAr[i] != pkt.dataAr[i]:
                    return False
        else:
            if (filter_el.base.frameID & filter_el.mask.frameID) != (pkt.frameID & filter_el.mask.frameID):
                return False
            if filter_el.base.dataLen == 0:
                return True
            # Compare data array byte by byte with mask
            for i in range(0, filter_el.base.dataLen):
                if (filter_el.base.dataAr[i] & filter_el.mask.dataAr[i]) != (pkt.dataAr[i] & filter_el.mask.dataAr[i]):
                    return False
        return True
