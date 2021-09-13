import asyncio
import datetime
import logging
import struct
import time
from typing import Any

from .EchonetLiteServer import res_handler, echonet_lite_server, echonet_lite_server_startup
from .class_name import CLASS_NAME
from .frame import Frame, Property
from .message_const import SETC, SETGET, GET, SETRES
from ..const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


def decode_prop_map(b: bytes):
    count = b[0]
    res = []
    if count < 16:
        for i in range(count):
            res.append(int(b[i + 1]))
    else:
        k = 0
        s = str(bin(int.from_bytes(b'\x01' + b[1:], byteorder="big")))[3:]
        for i in range(16):
            for j in range(8):
                if s[k] == "1":
                    res.append(0xF0 - j * 16 + i)
                k += 1

    return res


class EchonetLiteDevice:
    DEVICE_INFO_RANGE = range(0x8A, 0x8F)
    last_set = None
    discovered_node: list = []

    def __init__(self, identifier, host, gc, cc, ic, config: dict):
        self.host = host
        self.gc = gc
        self.cc = cc
        self.ic = ic
        self.last_fid = 0
        self.update_task = asyncio.Event()
        self.get_mapping = []
        self.set_mapping = []
        self.announce_mapping = []
        self._device_info = {"identifiers": {(DOMAIN, f'{identifier}_{gc}_{cc}_{ic}')}}
        self.props: dict[int, bytes] = {}
        self.config = config
        self.identifier = identifier

    async def send(self, esv: int, opc: list[Property], callback: callable = None, retry=0):
        f = Frame()
        f.DEOJGC = self.gc
        f.DEOJCC = self.cc
        f.DEOJIC = self.ic
        f.ESV = esv
        f.OPC = opc
        if esv == SETC:
            logging(f"sending to {self.host} {f}")
        if esv == SETGET:
            f.OPC2 = [Property(p.EPC) for p in f.OPC]
        await self.send_frame(f, callback, retry)

    async def send_frame(self, frame: Frame, callback: callable = None, retry=0):
        frame.TID = self.last_fid + 1
        self.last_fid += 1
        if self.last_fid >= 0xFF:
            self.last_fid = 0
        while retry >= 0:
            self.update_task.clear()
            if frame.ESV in [SETGET, SETC]:
                _LOGGER.debug(f"sending {frame.build_msg()}")
            echonet_lite_server.send(frame, self.host, callback)
            if callback is None:
                self.update_task.set()
                return
            try:
                await asyncio.wait_for(self.update_task.wait(), 5)
                break
            except asyncio.TimeoutError:
                retry -= 1
                if retry >= 0:
                    _LOGGER.debug(f"retry send data {frame}")
                else:
                    raise asyncio.TimeoutError()
                self.update_task.set()

    @staticmethod
    async def discovery(*, force=False):
        if not force and EchonetLiteDevice.last_set and time.time() - EchonetLiteDevice.last_set < 10:
            return EchonetLiteDevice.discovered_node
        EchonetLiteDevice.last_set = time.time()
        EchonetLiteDevice.discovered_node.clear()
        await echonet_lite_server_startup.wait()
        echonet_lite_server.discover()
        await asyncio.sleep(2)
        return EchonetLiteDevice.discovered_node

    def set_prop_mapping(self, frame: Frame, host: str, transport):
        self.update_task.set()
        opc_dict = dict((prop.EPC, prop.EDT) for prop in frame.OPC)
        self.announce_mapping = decode_prop_map(opc_dict[0x9D])
        self.set_mapping = decode_prop_map(opc_dict[0x9E])
        self.get_mapping = decode_prop_map(opc_dict[0x9F])

    def set_device_info(self, frame: Frame, host: str, transport):
        self.update_task.set()
        opc_dict = dict((prop.EPC, prop.EDT) for prop in frame.OPC)
        self._device_info["manufacturer_id"] = int.from_bytes(opc_dict[0x8A], byteorder="big")
        self._device_info["manufacturer"] = MANUFACTURER.get(int.from_bytes(opc_dict[0x8A], byteorder="big"), f"Unknown manufacturer ({opc_dict[0x8A].hex()})")
        self._device_info["business"] = opc_dict[0x8B].hex()
        self._device_info["model"] = opc_dict[0x8C].decode("ascii").rstrip("\x00")
        self._device_info["product_sn"] = opc_dict[0x8D].decode("ascii").rstrip("\x00")
        self._device_info["production_date"] = opc_dict[0x8E].hex()
        self._device_info["name"] = f"{CLASS_NAME.get(self.gc, {}).get(self.cc)}"
        # self._device_info["identifiers"] = {(DOMAIN, f'{self.host}_{self._device_info["manufacturer"]}_{self._device_info["model"]}_{self._device_info["product_sn"]}')}

    @property
    def device_info(self):
        return self._device_info

    def get_update_props(self) -> dict[int, int]:
        raise NotImplemented

    # @Throttle(TIME_BETWEEN_UPDATES)
    async def async_update(self):
        opc = [Property(epc) for epc in self.get_mapping if epc not in EchonetLiteDevice.DEVICE_INFO_RANGE]
        await self.send(GET, opc, self.update_props, retry=2)

    def update_props(self, frame: Frame, host: str, transport):
        self.update_task.set()
        _LOGGER.debug(f"{datetime.datetime.now()} response: {host} {frame}")
        if frame.ESV in [SETRES]:
            return
        for p in frame.OPC:
            self.props[p.EPC] = p.EDT

    def get_prop(self, epc, t=int):
        v = self.props.get(epc)
        if v is None:
            return v
        if t is int:
            return int.from_bytes(v, byteorder="big")
        if t is bytes:
            return v
        if t is str:
            return v.decode()
        return v

    async def async_set_props(self, props: list[(int, Any)]):
        data: list[Property] = []
        for (epc, value) in props:
            p = Property(epc)
            if value is None:
                pass
            if type(value) is bytes:
                p.EDT = value
            if type(value) is int or type(value) is float:
                value = int(value)
                p.EDT = value.to_bytes(int((len(hex(value)) - 1) / 2), byteorder="big")
            if type(value) is str:
                p.EDT = str.encode(value) + b'\0'

            data.append(p)
            self.props[epc] = p.EDT
        await self.send(SETC, data, self.update_props, 3)

    async def async_set_prop(self, epc: int, value: Any):
        await self.async_set_props([(epc, value)])


# Response handler for node discovery
def profile_node_handler(data: Frame, addr, transport):
    opc_dict = dict((prop.EPC, prop.EDT) for prop in data.OPC)
    prop_data = opc_dict[0xD6]
    identifier = opc_dict[0x83].hex()

    count = struct.unpack_from(f'>B', prop_data)[0]
    for i in range(count):
        arr = struct.unpack_from(f'>3B', prop_data, 1 + i * 3)
        EchonetLiteDevice.discovered_node.append(EchonetLiteDevice(
            identifier,
            addr[0],
            arr[0],
            arr[1],
            arr[2],
            {}
        ))


res_handler[0x0E] = profile_node_handler
