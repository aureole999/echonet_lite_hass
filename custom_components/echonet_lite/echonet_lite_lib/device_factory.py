from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device import get_config
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device_type.climate import *
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device_type.generic_device import *
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device_type.water_heater import *
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device_type.display import *
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.esv import GET

DEVICE_INFO_RANGE = range(0x8A, 0x8F)


class DeviceFactory:
    @staticmethod
    async def factory(identifier, host, gc, cc, ic):
        conf = get_config(gc, cc)
        if not conf.get("class_name"):
            this_device = GenericDevice(identifier, host, gc, cc, ic, conf)
        else:
            this_device = globals()[conf.get("class_name")](identifier, host, gc, cc, ic, conf)
        await this_device.send(GET, [Property(i) for i in DEVICE_INFO_RANGE], this_device.set_device_info)

        conf = get_config(gc, cc, this_device.device_info["manufacturer_id"], this_device.device_info["model"])
        if conf.get("class_name"):
            model_device = globals()[conf.get("class_name")](identifier, host, gc, cc, ic, conf)
            model_device._device_info = this_device._device_info
            this_device = model_device

        await this_device.send(GET, [Property(0x9D), Property(0x9E), Property(0x9F)], this_device.set_prop_mapping)
        print(f"{this_device.device_info}\n"
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
