from ... import EchonetLiteDevice


class WaterHeater(EchonetLiteDevice):

    def __init__(self, identifier, host, gc, cc, ic, config: dict):
        super().__init__(identifier, host, gc, cc, ic, config)

    async def set_temperature(self, value):
        await self.async_set_prop(0xD1, value)

    def get_temperature(self):
        return self.get_prop(0xD1)

    async def set_bath_auto_mode(self, value: bool):
        await self.async_set_prop(0xE3, 0x41 if value else 0x42)

    def get_bath_auto_mode(self):
        return self.get_prop(0xE3) == 0x41
