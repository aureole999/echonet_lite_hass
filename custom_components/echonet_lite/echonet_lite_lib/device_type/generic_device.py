from ... import EchonetLiteDevice


class GenericDevice(EchonetLiteDevice):
    def __init__(self, identifier, host, gc, cc, ic, config: dict):
        super().__init__(identifier, host, gc, cc, ic, config)
