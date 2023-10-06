
"""
Variable length frame

Tyep 1 Byte
    0xc0 Tyep
    bit5(frame type 0- standard frame (frame ID 2 bytes), 1-extended frame (frame ID 4 bytes))
    bit4(frame format 0- data frame, 1 remote frame)
    Bit0~3 Frame data length (0~8)

ExtFrame 4 byte
    1~8 bit (BYTE1) 
    9~16 bit (BYTE2) 
    17~24 bit (BYTE3) 
    25~29 bit (BYTE4)

StdFrame 2 byte - Standard Frame
    1~8 bit (BYTE1) 
    9~11 bit (BYTE2)
    
CAN data 8 bytes    

20 Bytes fixed frame

0 | TYPE              | 0x01-Data
1 | Frame type        | 0x01-Standard frame, 0x02-Extended frame
2 | Frame format      | Frame format 0x01- Data frame，0x02-Remote frame
3 | Frame ID data 1   | 1~8 bit, high bytes at the front, low bytes at the back
4 | Frame ID data 2   | 9~16 bit, high bytes at the front, low bytes at the back
5 | Frame ID data 3   | 17~24 bit, high bytes at the front, low bytes at the back
6 | Frame ID data 4   | 25~32 bit, high bytes at the front, low bytes at the back
7 | Frame data length | The data length of the CAN bus that is sent or accepted
8 | Frame data 1      | CAN sends or accepts data 1
9 | Frame data 2      | CAN sends or accepts data 2
10 | Frame data 3      | CAN sends or accepts data 3
11 | Frame data 4      | CAN sends or accepts data 4
12 | Frame data 5      | CAN sends or accepts data 5
13 | Frame data 6      | CAN sends or accepts data 6
14 | Frame data 7      | CAN sends or accepts data 7
15 | Frame data 8      | CAN sends or accepts data 8
16 | Reserved          | 0x00
    
"""

from CAN_BinHex import BinHexVal, BinHexAr
import json
import SMH


class CANPacket(object):
    def __init__(self):
        self.dataFrame = True # Frame type
        self.extFrame = False
        self.dataLen = 0
        self.frameID = 0
        self.dataAr = [0] * 8
        self._extHdrMask = 0x1FFFFFFF
        self._stdHdrMask = 0xffff
        self._byteMask = 0xff

    def set_type(self, tyep):
        self.dataFrame = True if (tyep & int("00010000", 2)) == 0 else False
        self.extFrame = True if (tyep & int("00100000", 2)) == 0 else False
        self.dataLen = tyep & int("00001111", 2)

    def set_frameId(self, idFrame):
        if self.extFrame:
            self.frameID = idFrame & self._extHdrMask
        else:
            self.frameID = idFrame & self._stdHdrMask

    def set_data(self, pos, val):
        self.dataAr[pos] = val & 0xFF

    def get_data(self, pos):
        return self.dataAr[pos]

    def __len__(self):
        return self.dataLen

    def load_bytestream(self, bytestream):
        # First byte is data
        self.extFrame = True if int.from_bytes(bytestream[1:2]) == SMH.CAN_FR_EXT else False
        self.dataFrame = True if int.from_bytes(bytestream[2:3]) == 1 else False

        if self.extFrame:
            fid = int.from_bytes(bytestream[6:7]) << 24
            fid = fid | (int.from_bytes(bytestream[5:6]) << 16)
            fid = fid | (int.from_bytes(bytestream[4:5]) << 8)
            fid = fid | int.from_bytes(bytestream[3:4])
            self.frameID = fid
        else:
            self.frameID = int.from_bytes(bytestream[3:7])

        self.dataLen = int.from_bytes(bytestream[7:8])
        for i in range(8, 8+self.dataLen):
            self.dataAr[i-8] = int.from_bytes(bytestream[i:i+1])

    def save_bytestream(self):
        bytestream = bytearray(17)
        bytestream[0] = 0
        bytestream[1] = SMH.CAN_FR_EXT & 0xFF if self.extFrame else SMH.CAN_FR_BASE & 0xFF
        bytestream[2] = 1 & 0xFF if self.dataFrame else 2 & 0xFF

        if self.extFrame:
            bytestream[6] = self.frameID >> 24 & 0xFF
            bytestream[5] = self.frameID >> 16 & 0xFF
            bytestream[4] = self.frameID >> 8 & 0xFF
            bytestream[3] = self.frameID & 0xFF

        bytestream[7] = self.dataLen & 0xFF
        for i in range(0, 7):
                bytestream[i+8] = self.dataAr[i]

        bytestream[16] = 0    # Reserved
        return bytestream

    def toJSON(self):
        return json.dumps(self.toDict(), sort_keys=True)

    def toDict(self):
        jDict = {
            SMH.FR_DATA: self.dataFrame,
            SMH.FR_ID_EXT: self.extFrame,
            SMH.FR_ID: self.frameID,
            SMH.FR_DATA_LEN: self.dataLen,
            SMH.FR_DATA_AR: self.dataAr
        }
        return jDict

    def fromDict(self, obj):
        # if SMH.FR_DATA in obj:
        self.dataFrame = obj[SMH.FR_DATA] if SMH.FR_DATA in obj else True

        # if SMH.FR_ID_EXT in obj:
        self.extFrame = obj[SMH.FR_ID_EXT] if SMH.FR_ID_EXT in obj else True
        self.frameID = obj[SMH.FR_ID]
        self.dataLen = obj[SMH.FR_DATA_LEN]
        self.dataAr = obj[SMH.FR_DATA_AR]

    def fromJSON(self, string):
        self.fromDict(json.loads(string))

    def __str__(self):
        return "ID:"+self.id_bin() + " DT:"+self.data_bin()

    def to_hex(self):
        return self.id_hex() + self.data_hex()

    def id_bin(self, delim=" ") -> str:
        bytes_len = 32 if self.extFrame else 16
        as_string = ""
        for i in range(bytes_len - 8, 0, -8):
            as_string += "{:08b}{}".format(self.frameID >> i & 0xFF, delim)
        as_string += "{:08b}".format(self.frameID & 0xFF)
        return as_string

    def id_hex(self, delim=" ") -> str:
        bytes_len = 32 if self.extFrame else 16
        as_string = ""
        for i in range(bytes_len - 8, 0, -8):
            as_string += "{:02X}{}".format(self.frameID >> i & 0xFF, delim)
        as_string += "{:02X}".format(self.frameID & 0xFF)
        return as_string

    def data_bin(self, delim=" ") -> str:
        s = ""
        if self.dataLen > 0:
            for i in range(0, self.dataLen - 1):
                s += "{:08b}{}".format(self.dataAr[i] & 0xFF, delim)
            s += "{:08b}".format(self.dataAr[self.dataLen - 1] & 0xFF)
        return s

    def data_hex(self, delim=" ") -> str:
        s = ""
        if self.dataLen > 0:
            for i in range(0, self.dataLen - 1):
                s += "{:02X}{}".format(self.dataAr[i] & 0xFF, delim)
            s += "{:02X}".format(self.dataAr[self.dataLen - 1] & 0xFF)
        return s