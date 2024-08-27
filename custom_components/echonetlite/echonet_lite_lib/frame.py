import logging
import struct
from dataclasses import dataclass

from .class_name import GROUP_NAME, CLASS_NAME
from .message_const import EHD1, EHD2, ESV_CODES

_LOGGER = logging.getLogger(__name__)


@dataclass
class Property:
    EPC: int
    EDT: bytes = b""


@dataclass
class Frame:
    EHD1: int = 0x10
    EHD2: int = 0x81
    TID: int = 0x01
    SEOJGC: int = 0x05
    SEOJCC: int = 0xFF
    SEOJIC: int = 0x01
    DEOJGC: int = 0
    DEOJCC: int = 0
    DEOJIC: int = 0
    ESV: int = 0
    OPC: list[Property] = None
    OPC2: list[Property] = None

    def is_valid(self):
        if self.EHD1 not in EHD1:
            raise ValueError(f'EHD1: {self.EHD1}')

        if self.EHD2 not in EHD2:
            raise ValueError(f'EHD2: {self.EHD2}')

        for (gc, cc) in [(self.SEOJGC, self.SEOJCC), (self.DEOJGC, self.DEOJCC)]:
            if gc not in GROUP_NAME:
                raise ValueError(f'EOJGC: {hex(gc)}')
            _LOGGER.debug(f'Group: {GROUP_NAME[gc]}')
            if gc != 0x0F and cc not in CLASS_NAME[gc]:
                raise ValueError(f'EOJCC: {hex(cc)}')
            _LOGGER.debug(f'Class: {CLASS_NAME[gc].get(cc, "User Defined Class")}')

        if self.ESV not in ESV_CODES:
            raise ValueError(f'ESV: {self.ESV}')
        _LOGGER.debug(f'ESV: {ESV_CODES[self.ESV]}')

    def build_msg(self) -> bytes:
        res = struct.pack('>2Bh8B', self.EHD1, self.EHD2, self.TID,
                          self.SEOJGC, self.SEOJCC, self.SEOJIC,
                          self.DEOJGC, self.DEOJCC, self.DEOJIC,
                          self.ESV, len(self.OPC))
        for p in self.OPC:
            res += struct.pack(f'B{len(p.EDT) + 1}p', p.EPC, p.EDT)
        if len(self.OPC) == 0:
            res += struct.pack(f'>B', 0)
        if self.OPC2:
            res += struct.pack(f'>B', len(self.OPC2))
            for p in self.OPC2:
                res += struct.pack(f'B{len(p.EDT) + 1}p', p.EPC, p.EDT)
            if len(self.OPC2) == 0:
                res += struct.pack(f'>B', 0)
        return res

    @staticmethod
    def decode_msg(byte):
        fix_head_format = struct.Struct(">2Bh8B")
        prop_text_len_format = struct.Struct(f'>B')

        arr = fix_head_format.unpack_from(byte, 0)
        msg = Frame(*arr[:-1], None)
        byte = byte[fix_head_format.size:]
        props = []
        for _ in range(arr[-1]):
            c = prop_text_len_format.unpack_from(byte, 1)[0] + 1
            props.append(Property(*struct.unpack_from(f'B{c}p', byte, 0)))
            byte = byte[c + 1:]
        msg.OPC = props
        return msg
