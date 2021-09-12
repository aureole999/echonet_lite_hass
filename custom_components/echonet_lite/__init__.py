import asyncio

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_DISCOVERY
from homeassistant.core import HomeAssistant
from homeassistant.custom_components.echonet_lite.echonet_lite_lib import EchonetLiteNodes
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.EchonetLiteNodes import EchonetLiteDevice
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.EchonetLiteServer import main, EchonetLiteServer, echonet_lite_server, echonet_lite_server_startup
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.device_factory import DeviceFactory
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
    """Set up TPLink from a config entry."""
    config_data = hass.data.setdefault(DOMAIN, {})
    discovered_node = await EchonetLiteDevice.discovery()
    hosts = dict([(i.identifier, i.host) for i in discovered_node])
    # if config_data is None and entry.data:
    #     config_data = entry.data
    # elif config_data is not None:
    #     hass.config_entries.async_update_entry(entry, data=config_data)
    #
    # device_registry = dr.async_get(hass)
    # tplink_devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    # device_count = len(tplink_devices)
    # hass_data: dict[str, Any] = hass.data[DOMAIN]
    # server = await main()
    # nodes.clear()
    # server.discover()
    # # await asyncio.sleep(1000)
    # hass_data["lights"] = [EchonetLiteNode(("192.168.1.1", 2020), 2, 124, 1)]
    host = hosts.get(entry.data["identifier"])
    if not host:
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
