import logging
import queue
import sys
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, QWaitCondition, QMutex, QObject, pyqtSlot
from gs_usb import GsUsbFrame, GsUsb

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


# class PktQueue (queue.Queue):


class CANReceiver:
    def __init__(self, buff: queue.Queue):
        super(CANReceiver, self).__init__()
        self.buff: queue.Queue = buff
        self.dev: GsUsb = None
        self.task = None
        self.stop_event = threading.Event()

    def stop_read(self):
        self.stop_event.set()
        logger.info("STOP receiver thread.")

    def start_read(self, dev: GsUsb):
        logger.info("START receiver thread.")
        self.dev = dev
        self.stop_event.clear()
        self.task = threading.Thread(target=self._read, daemon=True)
        self.task.start()

    def _read(self):

        #TODO:  Clear previosly received packets
        
        while not self.stop_event.is_set():
            can_frame = GsUsbFrame()
            if self.dev.device_flags is None:
                self.dev.device_flags = 0
            if self.dev.read(can_frame, 1000):
                self.buff.put(can_frame)
                logger.debug("Got CAN packet. Queue size = %d", self.buff.qsize())
        logger.debug("STOP reading CAN.")

    def is_empty(self):
        return self.buff.empty()

    def get_pkt(self, secs=0) -> GsUsbFrame:
        pkt = None
        try:
            if secs > 0:
                pkt = self.buff.get(block=True, timeout=secs)
            else:
                pkt = self.buff.get(block=False)

        except queue.Empty:
            # logger.debug("Queue is empty.")
            pkt = None

        return pkt
