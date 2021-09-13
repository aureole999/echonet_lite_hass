import asyncio
import logging
from asyncio import DatagramProtocol

from .frame import Frame, Property
from .message_const import GET

ENL_MULTICAST_ADDRESS = "224.0.23.0"

res_handler = {

}

_LOGGER = logging.getLogger(__name__)


def get_res_handler(data: Frame, host):
    if res_handler.get(f"{host}-{data.SEOJGC}-{data.SEOJCC}-{data.SEOJIC}-{data.TID}"):
        return res_handler.pop(f"{host}-{data.SEOJGC}-{data.SEOJCC}-{data.SEOJIC}-{data.TID}")
    attr = ["SEOJGC", "SEOJGG", "SEOJIC"]
    f = res_handler
    for a in attr:
        f = f.get(data.__dict__[a])
        if callable(f):
            return f
        if f is None:
            return None

    return f


class EchonetLiteServer(DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.node = dict()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        frame = Frame.decode_msg(data)
        f = get_res_handler(frame, addr[0])
        if callable(f):
            f(frame, addr, self.transport)
        else:
            _LOGGER.debug('Received %r from %s' % (frame, addr))

        self.transport.sendto(data, addr)

    def send(self, frame: Frame, host, callback: callable):
        if callback:
            res_handler[f"{host}-{frame.DEOJGC}-{frame.DEOJCC}-{frame.DEOJIC}-{frame.TID}"] = callback
        self.transport.sendto(frame.build_msg(), (host, 3610))

    def discover(self, echonet_class="", netif=""):

        frame = Frame()
        frame.OPC = [Property(0xD6), Property(0x83)]
        frame.TID = 0x01
        frame.DEOJGC = 0x0E
        frame.DEOJCC = 0xF0
        frame.DEOJIC = 0x00
        frame.ESV = GET

        _LOGGER.debug(frame)
        # Send message to multicast group and receive data
        _LOGGER.debug((netif if netif else ENL_MULTICAST_ADDRESS, 3610))
        _LOGGER.debug('Send %r to %s' % (frame.build_msg(), (netif if netif else ENL_MULTICAST_ADDRESS, 3610)))

        data = self.transport.sendto(frame.build_msg(), (netif if netif else ENL_MULTICAST_ADDRESS, 3610))


echonet_lite_server = EchonetLiteServer()
echonet_lite_server_startup = asyncio.Event()


async def main():
    _LOGGER.debug("Starting UDP server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: echonet_lite_server,
        local_addr=('0.0.0.0', 3610))
    echonet_lite_server_startup.set()
    return echonet_lite_server
    # try:
    #     await asyncio.sleep(3600)  # Serve for 1 hour.
    # finally:
    #     transport.close()
