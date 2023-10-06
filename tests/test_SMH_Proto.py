import json
from unittest import TestCase

import SMH_Proto
from SMH_Proto import CustomProto, ProtoSlice


class TestCustomProto(TestCase):
    def setUp(self):
        self.input_num = 2230240
        self.source = '{'\
            '"name":"SMH",' \
            '"descr":"",' \
            '"type":"frameid",'\
            '"id_slices":[' \
                     '{"name": "DestAddr", "start": 29, "len": 8,"short": "DA", "view_as": "dec"},' \
                     '{"name": "DestPort", "start": 21, "len": 4,"short": "DP", "view_as": "dec"},' \
                     '{"name": "SrcAddr", "start": 17, "len": 8,"short": "SA", "view_as": "dec"},' \
                     '{"name": "SrcPort", "start": 9, "len": 4,"short": "SP", "view_as": "dec"},' \
                     '{"name": "Command", "start": 5, "len": 5,"short": "C", "view_as": "dec"}]'\
            '}'

    def test_print_by_proto(self):
        out_val = 0
        print("Input source = {}".format(self.source))
        objs = json.loads(self.source)
        for obj in objs:
            print("Load slice = {}".format(obj["name"]))

        proto = CustomProto()
        SMH_Proto.proto_load(self.source)

        print(proto.to_string(self.input_num, "bin"))

        # self.assertEqual(proto.get_by_sname("FBT", input_num), 15)
        # self.assertEqual(proto.get_by_sname("SBT", input_num), 15)

        sl: ProtoSlice
        for sl in proto:
            if sl.short == "SA":
                print("Name {}, start {}, len {}".format(sl.name, sl.start, sl.len))
                lp, mp, tp = sl.cut_val(0xFFFFFFFF, 0xFFFFFFFF)
                print("LP \t{:08b} {:08b} {:08b} {:08b}".format(
                    (lp >> 24 & 0xFF).to_bytes(1, "big")[0],
                    (lp >> 16 & 0xFF).to_bytes(1, "big")[0],
                    (lp >> 8 & 0xFF).to_bytes(1, "big")[0],
                    (lp & 0xFF).to_bytes(1, "big")[0],
                ))
                print("MP \t{:08b} {:08b} {:08b} {:08b}".format(
                    (mp >> 24 & 0xFF).to_bytes(1, "big")[0],
                    (mp >> 16 & 0xFF).to_bytes(1, "big")[0],
                    (mp >> 8 & 0xFF).to_bytes(1, "big")[0],
                    (mp & 0xFF).to_bytes(1, "big")[0],
                ))
                print("TP \t{:08b} {:08b} {:08b} {:08b}".format(
                    (tp >> 24 & 0xFF).to_bytes(1, "big")[0],
                    (tp >> 16 & 0xFF).to_bytes(1, "big")[0],
                    (tp >> 8 & 0xFF).to_bytes(1, "big")[0],
                    (tp & 0xFF).to_bytes(1, "big")[0],
                ))

                out_val = sl.ins_val(self.input_num, 0x03)

        print("Original value = {}".format(self.input_num))
        print("Result value   = {}".format(out_val))

        self.assertEqual(self.input_num, out_val)

    def test_get_gaps(self):
        proto = SMH_Proto.proto_load(self.source)
        proto.delete("SA")

        gaps = proto.get_gaps()

        for gap in gaps:
            print(" GAP start {}, len {}, after {}".format(gap["start"], gap["len"], gap["after"]))
            self.assertEqual(gap["len"], 8)





