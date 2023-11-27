import binascii
import logging
import re
import sys
import SMH
from PyQt5.QtWidgets import QTreeWidgetItem
import CAN_Packet
from CAN_Packet import CANPacket
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import json

from SMH_Proto import CustomProto

MASK_OP_NONE = 0
MASK_OP_AND = 1
MASK_OP_OR = 2

ACTION_WAIT = 1
ACTION_SEND = 2

DELIMITER = ","

"""
Rule save file format

----------
0 - ruleId
1 
----------
2  -  Action. ACTION_WAIT - 1 or ACTION_SEND - 2
----------
3  -  timeout in msec
4  -  
5
6
----------
7  | TYPE              | 0x01-Data
8  | Frame type        | 0x01-Standard frame, 0x02-Extended frame
9 | Frame format      | Frame format 0x01- Data frame，0x02-Remote frame
10 | Frame ID data 1   | 1~8 bit, high bytes at the front, low bytes at the back
11 | Frame ID data 2   | 9~16 bit, high bytes at the front, low bytes at the back
12 | Frame ID data 3   | 17~24 bit, high bytes at the front, low bytes at the back
13 | Frame ID data 4   | 25~32 bit, high bytes at the front, low bytes at the back
14 | Frame data length | The data length of the CAN bus that is sent or accepted
15 | Frame data 1      | CAN sends or accepts data 1
16 | Frame data 2      | CAN sends or accepts data 2
17 | Frame data 3      | CAN sends or accepts data 3
18 | Frame data 4      | CAN sends or accepts data 4
19 | Frame data 5      | CAN sends or accepts data 5
20 | Frame data 6      | CAN sends or accepts data 6
21 | Frame data 7      | CAN sends or accepts data 7
22 | Frame data 8      | CAN sends or accepts data 8
23 | Reserved          | 0x00
----------

RuleID      - 2 bytes
"w" or "s"  - 1 byte
tout        - 4 byte
tyep        - 1 byte
frameid     - 2 or 4 byte
databytes   - 8 byte

"""

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class FilterElement(object):
    def __init__(self):
        # self.root = None
        self.parent = None
        self.child: list = []
        self.base = CANPacket()
        self.mask = CANPacket()
        self.action = SMH.ACTION_WAIT
        self.wait_time = 0
        # self.tree_item = None
        self.ruleId = 0
        self.view_link = None
        self.mask_empty = True
        self.descr = ""
        self.parent_id = 0
        self.name = ""
        self.use_data = False
        self.sort_order = 0

    def add_child(self, child_obj, ins_index = -1):
        if ins_index > 0 :
            self.child.insert(ins_index, child_obj)
        else:
            self.child.append(child_obj)
        child_obj.parent = self

    def get_children(self):
        return self.child

    def get_parent(self):
        return self.parent

    def has_child(self):
        return len(self.child) > 0

    def remove_child(self, param1):
        el = None
        if type(param1) == "int":
            for el in self.child:
                if el.ruleId == param1:
                    self.child.remove(el)
                    break
        elif isinstance(param1, FilterElement):
            el = self.child.remove(param1)
        else:
            raise ValueError("Param 1 should be type FilterElement, os int for ruleID")
        return el

    def id_bin_str(self) -> str:
        bit_ar = list(self.base.id_bin())
        if not self.mask_empty:
            mask_ar = self.mask.id_bin()
            for i in range(0, len(bit_ar)):
                if mask_ar[i] == "0":
                    bit_ar[i] = "-"
        return "".join(bit_ar)

    def id_hex_str(self) -> str:
        bit_ar = list(self.base.id_hex())
        if not self.mask_empty:
            mask_ar =  self.mask.id_hex()
            for i in range(0, len(bit_ar)):
                if mask_ar[i] == "0":
                    bit_ar[i] = "-"
        return "".join(bit_ar)

    def data_bin_str(self) -> str:
        bit_ar = []
        if self.use_data and self.base.dataLen > 0 :
            bit_ar = list(self.base.data_bin())
            if not self.mask_empty:
                mask_ar = list(self.mask.data_bin())
                for i in range(0, len(bit_ar)):
                    if mask_ar[i] == "0":
                        bit_ar[i] = "-"
        return "".join(bit_ar)

    def data_hex_str(self) -> str:
        bit_ar = []
        if self.use_data and self.base.dataLen > 0 :
            bit_ar = list(self.base.data_hex())
            if not self.mask_empty:
                mask_ar = list(self.mask.data_hex())
                for i in range(0, len(bit_ar)):
                    if mask_ar[i] == "0":
                        bit_ar[i] = "-"
        return "".join(bit_ar)

    #
    # def print_frameID(self, is_bin=True):
    #     if is_bin:
    #         base_bin_str =  "{:08b} {:08b} {:08b} {:08b}".format(self.base.frameID >> 24 & 0xFF,
    #                                                self.base.frameID >> 16 & 0xFF,
    #                                                self.base.frameID >> 8 & 0xFF,
    #                                                self.base.frameID & 0xFF
    #                                                )
    #         mask_bin_str =  "{:08b} {:08b} {:08b} {:08b}".format(self.mask.frameID >> 24 & 0xFF,
    #                                                self.mask.frameID >> 16 & 0xFF,
    #                                                self.mask.frameID >> 8 & 0xFF,
    #                                                self.mask.frameID & 0xFF
    #                                                )
    #         base_bin_str_ar = list(base_bin_str)
    #         if not self.mask_empty:
    #             for i in range(0, len(mask_bin_str)):
    #                 if mask_bin_str[i] == "0":
    #                     base_bin_str_ar[i] = '-'
    #         return "".join(base_bin_str_ar)
    #
    #     else:
    #         base_hex_str = "{:02X} {:02X} {:02X} {:02X}".format(self.base.frameID >> 24 & 0xFF,
    #                                                self.base.frameID >> 16 & 0xFF,
    #                                                self.base.frameID >> 8 & 0xFF,
    #                                                self.base.frameID & 0xFF
    #                                                )
    #         return base_hex_str
    #
    # def print_data(self, is_bin=True):
    #     ret_str = ""
    #     for i in range(0, self.base.dataLen):
    #         if is_bin:
    #             ret_str += "{:08b} ".format(self.base.dataAr[i])
    #         else:
    #             ret_str += "0x{:02X} ".format(self.base.dataAr[i])
    #
    #     return ret_str

    def load_bin_filter(self, bytestream):
        self.ruleId = int.from_bytes(bytestream[0:2], "big")
        self.action = SMH.ACTION_WAIT if int.from_bytes(bytestream[2:3], "big") == SMH.ACTION_WAIT else SMH.ACTION_SEND
        self.wait_time = int.from_bytes(bytestream[3:7], "big")
        self.base.load_bytestream(bytestream[7:24])
        self.mask.load_bytestream(bytestream[24:41])
        if self.mask.frameID > 0 and any(item > 0 for item in self.mask.dataAr):
            self.mask_empty = False

    def save_bin_filter(self):
        bytestream = bytearray(7)
        bytestream[0] = (self.ruleId >> 8) & 0xFF
        bytestream[1] = self.ruleId & 0xFF

        bytestream[2] = self.action & 0xFF

        bytestream[3] = (self.wait_time >> 24) & 0xFF
        bytestream[4] = (self.wait_time >> 16) & 0xFF
        bytestream[5] = (self.wait_time >> 8) & 0xFF
        bytestream[6] = self.wait_time & 0xFF

        # pkt_bytes = self.base.save_bytestream()
        # for i in range(7, 23):
        #     bytestream[i] = pkt_bytes[i - 7] & 0xFF
        bytestream.extend(self.base.save_bytestream())
        bytestream.extend(self.mask.save_bytestream())
        return bytestream

    def toJSON(self):
        return json.dumps(self.toDict(), sort_keys=True, indent=4)

    def toDict(self):
        jDict = {
            SMH.FL_NAME: self.name,
            SMH.FL_ID: self.ruleId,
            SMH.FL_PARENT_ID: self.parent.ruleId if self.parent is not None else None,
            SMH.FL_FILTER_FR: self.base.toDict(),
            SMH.FL_MASK_FR: self.mask.toDict(),
            SMH.FL_ACTION: SMH.ACT_TEXT_WAIT if self.action == SMH.ACTION_WAIT else SMH.ACT_TEXT_SEND,
            SMH.FL_TIMEOUT: self.wait_time,
            SMH.FL_DESCR: self.descr,
            SMH.FL_MASK_EMPTY: self.mask_empty,
            SMH.FL_USE_DATA: self.use_data,
            SMH.FL_SORT_ORDER: self.sort_order
        }
        return jDict

    def fromDict(self, obj: dict):
        self.name = obj[SMH.FL_NAME]
        self.ruleId = obj[SMH.FL_ID]
        self.mask_empty = obj[SMH.FL_MASK_EMPTY]
        #  Link to parent
        self.parent_id = obj[SMH.FL_PARENT_ID]
        self.base.fromDict(obj[SMH.FL_FILTER_FR])
        if not self.mask_empty:
            self.mask.fromDict(obj[SMH.FL_MASK_FR])
        self.action = SMH.ACTION_WAIT if obj[SMH.FL_ACTION] == SMH.ACT_TEXT_WAIT else SMH.ACTION_SEND
        self.wait_time = obj[SMH.FL_TIMEOUT]
        self.descr = obj[SMH.FL_DESCR]
        self.use_data = obj[SMH.FL_USE_DATA] if SMH.FL_USE_DATA in obj else True
        self.use_data = obj[SMH.FL_SORT_ORDER] if SMH.FL_SORT_ORDER in obj else -1


    def fromJSON(self, str):
        self.fromDict = json.loads(str)


class FilterTree:
    def __init__(self, tree_view: QtWidgets.QTreeWidget):
        self.tree_view = tree_view
        self.root_el = FilterElement()
        self.root_elements = self.root_el.child
        self.nextRuleID = 0
        self.set_header()
        self.use_proto = False
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(5, Qt.AscendingOrder)
        self.proto: CustomProto = None

    def set_proto(self, proto: CustomProto):
        self.use_proto = True
        self.proto = proto

    def set_header(self):
        self.tree_view.setColumnCount(6)

        self.tree_view.headerItem().setText(0, "ID")
        self.tree_view.headerItem().setText(1, "A")
        self.tree_view.headerItem().setText(2, "Time(ms)")
        self.tree_view.headerItem().setText(3, "FrameID")
        self.tree_view.headerItem().setText(4, "Data bytes")
        self.tree_view.setColumnHidden(5, True)
        # self.tree_view.headerItem().setSizeHint(0)

        header = self.tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        # header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        #  Width for 0 Column
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        header.resizeSection(0, 150)

        #  Width for 1 Column
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        header.resizeSection(1, 20)

    # def restore_tree(self, filename):
    #     parent_el: FilterElement = self.root_el
    #
    #     with open(filename, "rb") as file:
    #         while bytestream := file.read(41):
    #             filter_el = FilterElement()
    #             filter_el.load_bin_filter(bytestream)
    #             if filter_el.action == ACTION_WAIT:
    #                 self.el_insert(filter_el, self.root_el)
    #                 parent_el = filter_el
    #             else:
    #                 self.el_insert(filter_el, parent_el)
    #
    #     self.display_tree(self.root_el)

    def find_by_id(self, ID, root:FilterElement = None ):
        if root is None:
            root = self.root_el

        for el in root.get_children():
            if el.ruleId == ID:
                return el
            if el.has_child():
                ret = self.find_by_id(ID, el)
                if ret is not None:
                    return ret
        return None

    def display_tree(self, root: FilterElement = None, parent_item = None):
        if root is None:
            root = self.root_el

        for el in root.get_children():
            item = self.item_insert(el)
            if el.has_child:
                self.display_tree(el, item)

    def el_remove(self, el: FilterElement):
        parent = el.parent
        parent.remove_child(el)
        return el.view_link

    def el_create(self, jObj: dict, after_id = -1):
        el = FilterElement()
        el.fromDict(jObj)
        parent_el = self.root_el

        if el.parent_id != 0:
            parent_el: FilterElement = self.find_by_id(el.parent_id)

        if parent_el is not None:
            # if after_id >= 0:
            #     after_el: FilterElement = self.find_by_id(after_id)
            self.el_insert(el, parent_el, self.find_by_id(after_id) if after_id >= 0 else None)
            # parent_el.add_child(el, self.find_by_id(after_id) if after_id >= 0 else None)
        else:
            raise RuntimeError("Inconsistent rules tree. Cannot find parent by ID={}".format(el.parent_id))

        if self.nextRuleID <= el.ruleId:
            self.nextRuleID = el.ruleId + 1
        return el

    def el_insert(self, el: FilterElement, parent_el: FilterElement, after_el: FilterElement = None):

        ch_list: list = parent_el.get_children()
        ins_index = -1
        '''
           Process sort order for new element and all brothers
        '''
        if after_el is None:
            '''
               if element inserted at the end of list, just assign next sort iorder after last one
            '''
            if len(ch_list) > 0:
                after_el = ch_list[-1]
                el.sort_order = after_el.sort_order + 1
            else:
                el.sort_order = 1

        elif after_el.ruleId == parent_el.ruleId:
            '''
               if element inserted at the beginning of list. Shift sort order for all children
            '''
            el.sort_order = ch_list[1].sort_order if ch_list[1].sort_order >= 0 else 1
            for nb_el in ch_list:
                nb_el.sort_order += 1
            ins_index = 1
        else:
            '''
               if element inserted inside children list, increase sort order num after inserted position
            '''
            ins_index = 1
            found = False
            for nb_el in ch_list:
                if not found and nb_el.ruleId == after_el.ruleId:
                    found = True
                    el.sort_order = nb_el.sort_order + 1
                elif found:
                    nb_el.sort_order += 1
                else:
                    ins_index += 1

        parent_el.add_child(el, ins_index)
        # # parent_el.add_child(el, ins_index)
        # if self.nextRuleID <= el.ruleId:
        #     self.nextRuleID = el.ruleId + 1

    def item_remove(self, item):
        root_item = self.tree_view.invisibleRootItem()
        (item.parent() or root_item).removeChild(item)

    def item_insert(self, el: FilterElement):
        """
        Display elements content in tree row
        :param el:
        :return:
        """
        root_item = self.tree_view.invisibleRootItem()
        # parent_item = el.parent.view_link
        item = QTreeWidgetItem(el.parent.view_link or root_item)
        el.view_link = item

        item.setText(0, el.name)
        item.setData(0, Qt.UserRole, el)
        item.setData(0, Qt.TextAlignmentRole, Qt.AlignTop)

        item.setData(1, Qt.UserRole, el)
        item.setData(1, Qt.TextAlignmentRole, Qt.AlignTop)
        if el.action == ACTION_WAIT:
            item.setText(1, "W")
        else:
            item.setText(1, "S")

        # TODO: Insert Rule ID

        item.setText(2, str(el.wait_time))
        item.setData(2, Qt.TextAlignmentRole, Qt.AlignTop)
        item.setData(2, Qt.UserRole, el)
        logger.debug("Insert new filter rule. Name = %s, ruleid = %s, frame ID = %s", el.name, el.ruleId, el.id_hex_str())
        if self.use_proto:
            item.setText(3, self.proto.to_string(el.base.frameID))
        else:
            item.setText(3, el.id_bin_str())
        item.setData(3, Qt.UserRole, el)
        item.setText(4, el.data_hex_str())
        item.setData(4, Qt.UserRole, el)

        item.setText(5, str(el.sort_order))
        item.setData(5, Qt.UserRole, el)
        return item

    def increase_RuleID(self):
        self.nextRuleID += 1
        return self.nextRuleID

    def save_json_file(self, filename):
        js_array: list = []
        self._dump_child(js_array, self.root_el)
        out_file = open(filename, "w")
        json.dump(js_array, out_file, indent=4)
        out_file.close()

    def _dump_child(self, js_array: list, root_el: FilterElement):
        for el in root_el.child:
            js_array.append(el.toDict())
            if el.has_child:
                self._dump_child(js_array, el)

    def load_json_file(self, filename):
        self.nextRuleID = 0
        self.root_el = FilterElement()
        self.root_elements = self.root_el.child
        self.root_el.ruleId = 0
        self.tree_view.clear()
        try:
            in_file = open(filename, "r")
            jList = json.load(in_file)
            for jObj in jList:
                self.el_create(jObj)
            in_file.close()
            self.display_tree()
        except Exception as err:
            logger.error(err,exc_info=True)
