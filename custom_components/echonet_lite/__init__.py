import asyncio

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_DISCOVERY
from homeassistant.core import HomeAssistant
from .echonet_lite_lib import EchonetLiteNodes
from .echonet_lite_lib.EchonetLiteNodes import EchonetLiteDevice
from .echonet_lite_lib.EchonetLiteServer import main, EchonetLiteServer, echonet_lite_server, echonet_lite_server_startup
from .echonet_lite_lib.device_factory import DeviceFactory
from homeassistant.helpers.typing import ConfigType

DOMAIN = "echonet_lite"

PLATFORMS = ["sensor", "switch", "water_heater", "binary_sensor", "climate"]

HOST_SCHEMA = vol.Schema({vol.Required(CONF_HOST): cv.string})

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("nodes", default=[]): vol.All(
                    cv.ensure_list, [HOST_SCHEMA]
                ),
                vol.Optional(CONF_DISCOVERY, default=True): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

asyncio.create_task(main())


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the TP-Link component."""

    #
    # hass.data[DOMAIN] = {}
    # hass.data[DOMAIN]["config"] = conf

    # if conf is not None:
    # hass.async_create_task(
    #     hass.config_entries.flow.async_init(
    #         DOMAIN, context={"source": config_entries.SOURCE_IMPORT}
    #     )
    # )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config_data = hass.data.setdefault(DOMAIN, {})
    discovered_node = await EchonetLiteDevice.discovery()
    hosts = dict([(i.identifier, i.host) for i in discovered_node])
    host = hosts.get(entry.data["identifier"])
    
    retry = 3
    while not host and retry > 0:
        retry -= 1
        await asyncio.sleep(2)
        hosts = dict([(i.identifier, i.host) for i in await EchonetLiteDevice.discovery(force=True)])
        host = hosts.get(entry.data["identifier"])
    if not host:
        return False
    device = await DeviceFactory.factory(entry.data["identifier"], host, entry.data["gc"], entry.data["cc"], entry.data["ic"])
    config_data.update({entry.entry_id: device})
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    # Add services
    if len(device.config.get("services", {})) > 0:
        for k, v in device.config.get("services", {}).items():
            f = getattr(device, v.get("func"))
            hass.services.async_register(DOMAIN, f"{v.get('name')}", f)

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
