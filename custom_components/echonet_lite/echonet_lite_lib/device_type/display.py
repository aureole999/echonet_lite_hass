import struct

from homeassistant.custom_components.echonet_lite import EchonetLiteDevice


class Display(EchonetLiteDevice):
    def __init__(self, identifier, host, gc, cc, ic, config: dict):
        super().__init__(identifier, host, gc, cc, ic, config)

    async def async_notify(self, call):
        value = call.data.get("text", "")
        b = value.encode("utf-8")
        while len(b) > 244:
            value = value[:-1]
            b = value.encode("utf-8")

        prop = struct.pack(">3B", len(b), 0x08, 0x00)

        await self.async_set_prop(0xB3, prop + b)
