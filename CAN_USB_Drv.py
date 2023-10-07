import copy
import logging
import queue
import sys
import threading

# import serial as serial
from PyQt5.QtWidgets import QMessageBox
# from serial import SerialException
# import usb
# import can

import time

from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame
from gs_usb.constants import (
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
)
from gs_usb.gs_usb_structures import DeviceMode
from usb.core import USBError

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(module)s-%(funcName)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)

# https://github.com/jxltom/gs_usb
# https://docs.python.org/3/library/exceptions.html

# gs_usb mode
GS_CAN_MODE_RESET = 0
GS_CAN_MODE_START = 1

# gs_usb control request
_GS_USB_BREQ_HOST_FORMAT = 0
_GS_USB_BREQ_BITTIMING = 1
_GS_USB_BREQ_MODE = 2
_GS_USB_BREQ_BERR = 3
_GS_USB_BREQ_BT_CONST = 4
_GS_USB_BREQ_DEVICE_CONFIG = 5


class ConnectError(Exception):
    def __init__(self, message, err, devinfo=None):
        # Call the base class constructor with the parameters it needs
        self.err = err
        self.devinfo = devinfo
        super().__init__(message)


class CANLibDrv(object):
    def __init__(self):
        self.full_port_name = ""
        self.dev: GsUsb = None
        self.bitrate = 500000
        self.device_flags = 0
        self.info = {
            "bus": "",
            "addr": "",
            "sn": "",
            "info": "",
            "cap": ""
        }
        self.buff = queue.Queue()
        self.cur_thread = None
        self.is_started = False

    def connect(self, dev=None):
        # Find our device
        if dev is None:
            devs = GsUsb.scan()
            if len(devs) == 0:
                logger.error("Can not find gs_usb device")
                raise ConnectError("Can not find gs_usb device", 1)
            logger.debug("Scan found USB device %s", self.dev)
            self.dev = devs[0]
        else:
            self.dev = GsUsb.find(dev.bus, dev.address)
            logger.debug("Found USB device %s", self.dev)

        # Configuration
        if self.bitrate > 0:
            if not self.dev.set_bitrate(self.bitrate):
                logger.error("Can not set bitrate for gs_usb")
                raise ConnectError("Can not set bitrate for gs_usb", 2)
        self.device_flags = self.dev.device_flags
        return self.dev

    def start(self, bitrate=0):
        if self.dev is None:
            raise ConnectError("Start processing w/o device connection", 3)

        if bitrate > 0:
            self.bitrate = bitrate
            if self.bitrate > 0:
                if not self.dev.set_bitrate(self.bitrate):
                    logger.error("Can not set bitrate for gs_usb")
                    raise ConnectError("Can not set bitrate for gs_usb", 2)

        # Start device
        # flags = self.dev.gs_usb.device_capability.feature
        # flags &= self.device_capability.feature
        self.dev.device_flags = 0
        mode = DeviceMode(GS_CAN_MODE_START, 0)
        self.dev.gs_usb.ctrl_transfer(0x41, _GS_USB_BREQ_MODE, 0, 0, mode.pack())

        # Start worker
        self.is_started = True

    def stop(self):
        if self.dev is not None:
            self.dev.stop()
        self.is_started = False

    def send(self, canid, data_len, data, canflag=CAN_EFF_FLAG):
        if self.dev is None:
            raise ConnectError("Start processing w/o device connection", 3)

        can_frame = GsUsbFrame(can_id=canid | canflag, data=data[0:data_len])
        self.dev.device_flags = self.device_flags if self.device_flags is not None else 0
        if not self.dev.send(can_frame):
            raise ConnectError("Send Error", 4)

    def rcv(self, tout=100):
        iframe = GsUsbFrame()
        if self.dev.read(iframe, tout):
            return iframe
        return None

    def status(self):
        if self.dev is None:
            return False
        try:
            data = self.dev.device_info
            if data:
                return True

        except USBError as err:
            logger.warning(err)
            # self.dev = None
            pass

        return False

    def get_info(self):
        self.info["info"] = "fw v." + str(self.dev.device_info.fw_version/10.0) + " :" +\
                             " hw v." + str(self.dev.device_info.hw_version /10.0)
        self.info["sn"] = self.dev.serial_number
        self.info["addr"] = self.dev.address
        self.info["bus"] = self.dev.bus
        # self.info["cap"] = self.dev.device_capability()
        return None if self.dev is None else self.info

