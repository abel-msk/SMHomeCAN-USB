
BASE_ANY = 0
BASE_INT = 1
BASE_HEX = 2
BASE_BIN = 3


class BinHexVal(object):
    def __init__(self, val, base=BASE_ANY):
        self.value = 0
        self.mask = int("11111111", 2)

        if base == BASE_INT:
            self.set(val)
        elif base == BASE_HEX:
            self.set_as_hex(val)
        elif base == BASE_BIN:
            self.set_as_bin(val)
        elif base == BASE_ANY:
            if type(val) is int:
                self.set(val)
            elif val.isdigit():
                self.set_as_bin(val)
            else:
                self.set_as_hex(val)

    def set(self, val):
        self.value = val & self.mask

    def set_as_bin(self, bin_val):
        if len(bin_val) > 8:
            self.value = int(bin_val[len(bin_val) - 8:len(bin_val)], 2)
        else:
            self.value = int("{:08s}".format(bin_val), 2)

    def set_as_hex(self, hex_val):
        if len(hex_val) > 2:
            self.value = int(hex_val[len(hex_val) - 2:len(hex_val)], 16)
        else:
            self.value = int("0"+hex_val)

    def __eq__(self, other):
        return self.value == other.value

    def get_as_bin(self):
        retVAL = "{:08b}".format(self.value)
        return retVAL[len(retVAL) - 8:len(retVAL)]

    def get_as_hex(self):
        retVAL = "{:02X}".format(self.value)
        return retVAL[len(retVAL) - 2:len(retVAL)]

    def get(self):
        return self.value

class BinHexAr(object):
    def __init__(self):
        self.bytes_array = []
        self.mask = int("11111111", 2)

    def append_int(self, value, bytes_len=2):
        for i in range(0, bytes_len*8, 8):
            byte = BinHexVal((value >> i) & self.mask, BASE_INT)
            self.bytes_array.insert(1, byte)

    def append_byte(self, value, base=BASE_INT):
        byte = BinHexVal(value & self.mask, base)
        self.bytes_array.append(byte)

    def get_byte(self, pos):
        return self.bytes_array[pos].get()

    def set_byte(self, byte, pos):
        self.bytes_array[pos].set(byte)

    def load_bin(self, value):
        self.bytes_array = []
        k, m = divmod(len(value), 8)
        if m > 0:
            newByte = BinHexVal(value[0:m], BASE_BIN)
            self.bytes_array.append(newByte)

        for i in range(m, len(value), 8):
            newByte = BinHexVal(value[i:i + 8 - 1], BASE_BIN)
            self.bytes_array.append(newByte)

    def load_hex(self, value):
        self.bytes_array = []
        k, m = divmod(len(value), 2)
        if m > 0:
            newByte = BinHexVal(value[0:m], BASE_HEX)
            self.bytes_array.append(newByte)

        for i in range(m, len(value), 2):
            newByte = BinHexVal(value[i:i + 2], BASE_HEX)
            self.bytes_array.append(newByte)

    def print_hex(self):
        for byte in self.bytes_array:
            print("Byte:%s\n", byte.get_as_bin())
