import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.EchonetLiteNodes import discovered_node
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.EchonetLiteServer import echonet_lite_server


class SmartDevice:
    def __init__(self):
        pass


async def async_get_discoverable_devices(hass: HomeAssistant) -> dict[str, SmartDevice]:
    """Return if there are devices that can be discovered."""

    async def discover() -> dict[str, SmartDevice]:
        discovered_node.clear()
        echonet_lite_server.discover()
        await asyncio.sleep(1)
        print(discovered_node)
        d = dict(zip((i.addr for i in discovered_node), discovered_node))
        return d

    return await discover()
    # return {"test": SmartDevice()}
