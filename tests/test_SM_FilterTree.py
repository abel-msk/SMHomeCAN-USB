import json
from unittest import TestCase
import SMH_FilterTree
from SMH_FilterTree import FilterElement

TEST_FN = "sline.bfd"
TEST2_FN = "dbline2.bfd"

class TestFilterElement(TestCase):
    def setUp(self):
        self.TestBinValue = "1111101010"
        self.TestHexValue = "AFF"

        self.el = FilterElement()
        self.el.action = SMH_FilterTree.ACTION_WAIT
        self.el.wait_time = 10000
        self.el.ruleId = 21
        self.el.parent = None
        self.el.base.extFrame = True
        self.el.base.dataLen = 2
        self.el.base.frameID = 0x0f111111
        self.el.base.set_data(0, 0x11)
        self.el.base.set_data(1, 0x12)
        self.el.mask_empty = False

        self.el.mask.extFrame = True
        self.el.mask.frameID = 0x0f111111
        self.el.mask.dataLen = 2
        self.el.mask.set_data(0, 0xFF)
        self.el.mask.set_data(1, 0xFF)


        self.create_test_file()

    def create_test_file(self):
        with open(TEST_FN, "wb") as file:
            byte_ar = self.el.save_bin_filter()
            file.write(byte_ar)
        print("File created")

    def read_test_file(self):
        el2 = FilterElement()
        with open(TEST_FN, "rb") as file:
            bytestream = file.read(24)
            el2.load_bin_filter(bytestream)
        return el2

    def test_load_bin_filter(self):
        el2 = self.read_test_file()

        print("el2.ruleId: {:X}".format(el2.ruleId))
        self.assertEqual(el2.ruleId, self.el.ruleId)

        print("el2.action: {:X}".format(el2.action))
        self.assertEqual(el2.action, self.el.action)

        print("el2.wait_time: {}".format(el2.wait_time))
        self.assertEqual(el2.wait_time, self.el.wait_time)

        print("el2.base.extFrame: {}".format(el2.base.extFrame))
        self.assertEqual(el2.base.extFrame, self.el.base.extFrame)

        print("el2.base.extFrame: {}".format(el2.base.extFrame))
        self.assertEqual(el2.base.extFrame, self.el.base.extFrame)

        print("el2.base.frameID: {:X}".format(el2.base.frameID))
        self.assertEqual(el2.base.frameID, self.el.base.frameID)

        print("el2.base.dataLen: {}".format(el2.base.dataLen))
        self.assertEqual(el2.base.dataLen, self.el.base.dataLen)

        for i in range(0, 7):
            print("el2.base.dataAr[{}]: {}".format(i, el2.base.dataAr[i]))
            self.assertEqual(el2.base.dataAr[i], self.el.base.dataAr[i])

    def test_save_bin_filter(self):
        with open(TEST_FN, "wb") as file:
            byte_ar = self.el.save_bin_filter()
            file.write(byte_ar)

        print("File created")

    def test_save_filter_tree(self):
        el = FilterElement()
        el.action = SMH_FilterTree.ACTION_WAIT
        el.wait_time = 10000
        el.ruleId = 21

        #  Base bits for filter 1
        el.base.extFrame = True
        el.base.dataLen = 2
        el.base.frameID = 0x0EEEEEEE
        el.base.set_data(0, 0x11)
        el.base.set_data(1, 0x12)

        #  Mask bits for filter 1
        el.mask.extFrame = el.base.extFrame
        el.mask.dataLen = el.base.dataLen
        el.mask.frameID = 0x000000FF
        el.mask.set_data(0, 0xFF)
        el.mask.set_data(1, 0x00)

        # Filter 2
        el2 = FilterElement()
        el2.action = SMH_FilterTree.ACTION_SEND
        el2.wait_time = 80000
        el2.ruleId = 21

        el2.base.extFrame = True
        el2.base.dataLen = 3
        el2.base.frameID = 0x01234567
        el2.base.set_data(0, 0x11)
        el2.base.set_data(1, 0x12)
        el2.base.set_data(2, 0x13)

        el2.mask.extFrame = el2.base.extFrame
        el2.mask.dataLen = el2.base.dataLen
        el2.mask.frameID = 0x00FF0000
        el2.mask.set_data(0, 0x00)
        el2.mask.set_data(1, 0x00)
        el2.mask.set_data(2, 0x00)

        with open(TEST2_FN, "wb") as file:
            byte_ar = el.save_bin_filter()
            file.write(byte_ar)
            byte_ar = el2.save_bin_filter()
            file.write(byte_ar)

    def test_load_filter_tree(self):
        el1 = FilterElement()
        el2 = FilterElement()
        with open(TEST2_FN, "rb") as file:
            bytestream1 = file.read(41)
            el1.load_bin_filter(bytestream1)
            bytestream2= file.read(41)
            el2.load_bin_filter(bytestream2)

        print("el1.base.frameID: {:04X}".format(el1.base.frameID))
        print("el2.base.frameID: {:04X}".format(el2.base.frameID))

        print("el1.mask.frameID: {:04X}".format(el1.mask.frameID))
        print("el2.mask.frameID: {:04X}".format(el2.mask.frameID))

    # def test_save_json(self):
    #     el = self.read_test_file()
    #     print(el.toJSON())

    def test_load_json(self):
        json_str = self.el.toJSON()
        el_obj = json.loads(json_str)
        el2 = FilterElement()
        el2.fromDict(el_obj)

        print("el2.ruleId: {:X}".format(el2.ruleId))
        self.assertEqual(el2.ruleId, self.el.ruleId)

        print("el2.action: {:X}".format(el2.action))
        self.assertEqual(el2.action, self.el.action)

        print("el2.wait_time: {}".format(el2.wait_time))
        self.assertEqual(el2.wait_time, self.el.wait_time)

        print("el2.base.extFrame: {}".format(el2.base.extFrame))
        self.assertEqual(el2.base.extFrame, self.el.base.extFrame)

        print("el2.base.extFrame: {}".format(el2.base.extFrame))
        self.assertEqual(el2.base.extFrame, self.el.base.extFrame)

        print("el2.base.frameID: {:X}".format(el2.base.frameID))
        self.assertEqual(el2.base.frameID, self.el.base.frameID)

        print("el2.base.dataLen: {}".format(el2.base.dataLen))
        self.assertEqual(el2.base.dataLen, self.el.base.dataLen)

        for i in range(0, 7):
            print("el2.base.dataAr[{}]: {}".format(i, el2.base.dataAr[i]))
            self.assertEqual(el2.base.dataAr[i], self.el.base.dataAr[i])

        print("el2.mask.frameID: {:X}".format(el2.mask.frameID))
        self.assertEqual(el2.mask.frameID, self.el.mask.frameID)

