import logging

from .device import get_config
from .device_type.climate import *
from .device_type.display import *
from .device_type.generic_device import *
from .device_type.water_heater import *
from .frame import Property
from .message_const import GET

DEVICE_INFO_RANGE = range(0x8A, 0x8F)
_LOGGER = logging.getLogger(__name__)


class DeviceFactory:
    @staticmethod
    async def factory(identifier, host, gc, cc, ic):
        conf = get_config(gc, cc)
        if not conf.get("class_name"):
            this_device = GenericDevice(identifier, host, gc, cc, ic, conf)
        else:
            this_device = globals()[conf.get("class_name")](identifier, host, gc, cc, ic, conf)
        await this_device.send(GET, [Property(i) for i in DEVICE_INFO_RANGE], this_device.set_device_info, retry=3)

        conf = get_config(gc, cc, this_device.device_info["manufacturer_id"], this_device.device_info["model"])
        if conf.get("class_name"):
            model_device = globals()[conf.get("class_name")](identifier, host, gc, cc, ic, conf)
            model_device._device_info = this_device._device_info
            this_device = model_device

        await this_device.send(GET, [Property(0x9D), Property(0x9E), Property(0x9F)], this_device.set_prop_mapping, retry=3)
        _LOGGER.debug(f"{this_device.device_info}\n"
                      f"Gettable properties: {[hex(e) for e in this_device.get_mapping]}\n"
                      f"Settable properties: {[hex(e) for e in this_device.set_mapping]}")
        # await this_device.async_update()

        # Prevent import being optimized
        # noinspection PyUnreachableCode
        if False:
            # noinspection PyArgumentList
            GenericDevice()
            # noinspection PyArgumentList
            Climate()
            # noinspection PyArgumentList
            WaterHeater()
            # noinspection PyArgumentList
            Display()

        return this_device
