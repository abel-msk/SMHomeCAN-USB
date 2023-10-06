from unittest import TestCase
from CAN_BinHex import BinHexVal, BinHexAr


class TestBinHexVal(TestCase):
    def setUp(self):
        self.TestBinValue = "1111101010"
        self.TestHexValue = "AFF"

    def test_as_bin(self):
        obj = BinHexVal()
        obj2 = BinHexVal()
        print("Input : ", self.TestBinValue)
        obj.as_bin(self.TestBinValue)
        print("Bin Byte : ", obj.get_as_bin())
        self.assertEqual(obj.get_as_bin(), "11101010")

        print("Input : ", self.TestHexValue)
        obj2.as_hex(self.TestHexValue)
        print("Hex Byte : ", obj2.get_as_hex())
        self.assertEqual(obj2.get_as_hex(), "FF")
    # def test_as_hex(self):
    #     self.fail()
    #
    # def test_get_as_bin(self):
    #     self.fail()
