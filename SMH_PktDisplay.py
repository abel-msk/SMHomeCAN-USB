import collections
import json
import logging
import sys
from collections.abc import Iterator

from CAN_Packet import CANPacket
from SMH_Proto import CustomProto

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='[%(levelname)s] %(name)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


