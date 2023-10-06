from unittest import TestCase
from CAN_USB_Drv import CANConnector

class TestCANConnector(TestCase):
    def test_scan_open(self):
        c = CANConnector()
        c.scan_open(500000)