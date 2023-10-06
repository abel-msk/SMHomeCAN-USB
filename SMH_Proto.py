import collections
import json
import logging
import sys
from collections.abc import Iterator

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)

PROTO_TYPE_FRANE_ID = "frame_id"

PROTO_NAME = "name"
PROTO_DESCR = "descr"
PROTO_ID_SLICES = "id_slices"
PROTO_TYPE = "type"
NAME = "name"
START = "start"
LEN = "len"
SHORT = "short"
VIEW_AS = "view_as"  # TODO: default view as bin, hex, dec

VIEW_TYPES = ["bin", "dec", "hex"]

class ProtoSlice(object):
    def __init__(self):
        self.start = 0
        self.len = 0
        self.data = 0
        self.name = ""
        self.short = ""
        self._const = 0xFFFFFFFF
        self.view_as = VIEW_TYPES[2]

    def dub(self):
        sl: ProtoSlice = ProtoSlice()
        sl.name = self.name
        sl.short = self.short
        sl.start = self.start
        sl.len = self.len
        return sl

    def ext_val(self, src_num: int):
        return_data = src_num >> (self.start - self.len) & (0xFFFFFFFF >> 32 - self.len)
        str_bin = "{:08b}".format(return_data & 0xFF)
        str_hex = "0x{:02x}".format(return_data & 0xFF)
        # logger.debug("Proto slice %s, start=%s, len=%s, \t| %s | %s |", self.name, self.start, self.len, str_hex,
        #              str_bin)
        return return_data

    def cut_val(self, src_num: int, slice_val):
        lead_part = src_num & (0xFFFFFFFF << self.start)
        tail_part = src_num & (0xFFFFFFFF >> (32 - self.start + self.len))
        mid_part = (slice_val & (0xFFFFFFFF >> 32 - self.len)) << self.start - self.len

        logger.debug("lead part {:08b} {:08b} {:08b} {:08b}".format(
            (lead_part >> 24 & 0xFF).to_bytes(1, "big")[0],
            (lead_part >> 16 & 0xFF).to_bytes(1, "big")[0],
            (lead_part >> 8 & 0xFF).to_bytes(1, "big")[0],
            (lead_part & 0xFF).to_bytes(1, "big")[0]
        ))

        logger.debug("mid part {:08b} {:08b} {:08b} {:08b}".format(
            (mid_part >> 24 & 0xFF).to_bytes(1, "big")[0],
            (mid_part >> 16 & 0xFF).to_bytes(1, "big")[0],
            (mid_part >> 8 & 0xFF).to_bytes(1, "big")[0],
            (mid_part & 0xFF).to_bytes(1, "big")[0],
        ))

        logger.debug("mid part {:08b} {:08b} {:08b} {:08b}".format(
            (tail_part >> 24 & 0xFF).to_bytes(1, "big")[0],
            (tail_part >> 16 & 0xFF).to_bytes(1, "big")[0],
            (tail_part >> 8 & 0xFF).to_bytes(1, "big")[0],
            (tail_part & 0xFF).to_bytes(1, "big")[0],
        ))

        return lead_part, mid_part, tail_part

    def ins_val(self, src_num: int, slice_val):
        lp, mp, tp = self.cut_val(src_num, slice_val)
        return lp | mp | tp

    def toDict(self) -> dict:
        return  {
            NAME: self.name,
            START: self.start,
            LEN: self.len,
            SHORT: self.short,
            VIEW_AS: self.view_as
        }


class ProtoIterator(Iterator):
    def __init__(self, slices: list):
        self._current_index = -1
        self.slices = slices

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self._current_index += 1
            return self.slices[self._current_index]
        except IndexError:
            raise StopIteration


class CustomProto(object):
    def __init__(self):
        self.name = ""
        self.descr = ""
        self.slices = []
        self.full_ext_id_len = 29

    def __iter__(self) -> ProtoIterator:
        return ProtoIterator(self.slices)

    def dub(self):
        new_proto: CustomProto = CustomProto()
        new_proto.name = self.name
        new_proto.descr = self.descr
        for sl in self.slices:
            new_proto.append(sl.dub())
        return new_proto

    def sort(self):
        self.slices.sort(key=lambda element: element.start, reverse=True)

    def append(self, sl: ProtoSlice, sort=True):
        self.slices.append(sl)
        if sort:
            self.sort()

    def insert(self, name: str, short: str = "", start: int = 0, len: int = 1):
        sl: ProtoSlice
        new_sl = ProtoSlice()
        new_sl.name = name
        new_sl.short = short if short != "" else name[0:3]
        new_sl.start = start
        new_sl.len = len

        if start == 0:
            self.append(new_sl, sort=False)
            return new_sl
        else:
            count = 0
            for sl in self.slices:
                if sl.start < start:
                    logger.debug("Found position to insert start %s/%s", sl.start, sl.len)
                    self.slices.insert(count, new_sl)
                    return new_sl
                count += 1
            self.slices.insert(0, new_sl)

    def delete(self, sname:str):
        for sl in self.slices:
            if sl.short == sname:
                self.slices.remove(sl)
                return sl
        raise KeyError("Slice with short name {} not found.".format(sname))

    def to_string(self, frameID, format="bin") -> str:
        if len(self.slices) < 1:
            return ""

        if format not in VIEW_TYPES:
            raise ValueError("Incorrect parameter 'format'. Possible values is {}".format(
                " ".join([str(x) for x in VIEW_TYPES])))

        out_str: str = ""
        sl: ProtoSlice
        for sl in self.slices:
            if format == "bin":
                format_line = " {}:{:0" + str(sl.len) + "b}"
                out_str += format_line.format(sl.short, sl.ext_val(frameID))
            elif format == "hex":
                out_str += " {}:{:02X}".format(sl.short, sl.ext_val(frameID))
            elif format == "dec":
                out_str += " {}:{}".format(sl.short, sl.ext_val(frameID))

        logger.debug("Prepare protocol view: %s, for frame ID %s ", out_str, frameID)
        return out_str[1:]

    def get_index(self, short):
        count = 0
        sl: ProtoSlice
        for sl in self.slices:
            if sl.short == short:
                return count
            count += 1
        raise KeyError("Slice with short name {} not found.".format(short))

    def get_slice(self, short: str) -> ProtoSlice:
        sl: ProtoSlice
        for sl in self.slices:
            if sl.short == short:
                return sl
        raise KeyError("Slice with short name {} not found.".format(short))

    def get_slice_pos(self, pos: int) -> ProtoSlice:
        sl: ProtoSlice
        for sl in self.slices:
            if sl.start >= pos and (sl.start - sl.len <= pos):
                return sl
        raise KeyError("Slice for pos {} not found.".format(pos))

    # def extract_by_sname(self, sname, frameid):
    #     for sl in self.slices:
    #         if sl.short == sname:
    #             return sl.extract(frameid)
    #     raise ValueError("Protocol slice with name {}, not found.".format(sname))
    #
    # def insert_by_sname(self, sname, frameid):
    #     for sl in self.slices:
    #         if sl.short == sname:
    #             return sl.insert(frameid)
    #     raise ValueError("Protocol slice with name {}, not found.".format(sname))

    def get_gaps(self) -> list:
        gaps = []
        last_pos = self.full_ext_id_len
        sl: ProtoSlice
        for sl in self.slices:
            if sl.start < last_pos:
                gaps.append({"start": last_pos, "len": last_pos - sl.start, "after": sl.short})
            last_pos = sl.start - sl.len
        return gaps

    def toJson(self):
        pass

    def toDict(self):
        sl_ar = []
        for sl in self.slices:
            sl_ar.append(sl.toDict())

        jDict = {
            PROTO_NAME: self.name,
            PROTO_DESCR: self.descr,
            PROTO_TYPE: PROTO_TYPE_FRANE_ID,
            PROTO_ID_SLICES: sl_ar
        }

        return jDict


def proto_file_load(filename: str) -> CustomProto:
    proto = None
    try:
        in_file = open(filename, "r")
        jObj = json.load(in_file)
        proto = from_json(jObj)
    except Exception as err:
        logger.error(err)
        raise err
    return proto


def proto_load(stream: str):
    proto_obj = from_json(json.loads(stream))
    return proto_obj


def from_json(jDict: dict) -> CustomProto:
    if jDict[PROTO_TYPE] == PROTO_TYPE_FRANE_ID:
        proto_obj = CustomProto()
    else:
        proto_obj = CustomProto()

    proto_obj.name = jDict[PROTO_NAME]
    proto_obj.descr = jDict[PROTO_DESCR]
    for obj in jDict[PROTO_ID_SLICES]:
        sl = ProtoSlice()
        sl.name = obj[NAME]
        sl.start = obj[START]
        sl.len = obj[LEN]
        sl.short = obj[SHORT] if SHORT in obj.keys() else sl.name[0:3]
        sl.view_as = obj[VIEW_AS] if VIEW_AS in obj.keys() else "hex"
        proto_obj.append(sl)

    return proto_obj


def proto_save(proto: CustomProto, theFileName: str):
    out_file = open(theFileName, "w")
    json.dump(proto.toDict(), out_file, indent=4)
    out_file.close()


