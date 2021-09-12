"""Support for Daikin AC sensors."""
import asyncio
import datetime
from datetime import timedelta
from typing import Any

from homeassistant.components.switch import SwitchEntity, _LOGGER
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
)
from . import EchonetLiteDevice
from .const import DOMAIN
from .coordinator import MyDataUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    echonet_node: EchonetLiteDevice = hass.data[DOMAIN].get(entry.entry_id)
    set_mapping = echonet_node.set_mapping
    switches = echonet_node.config.get("switches", {})
    coordinator = await MyDataUpdateCoordinator.factory(entry.entry_id, hass, _LOGGER, "switch", update_interval=timedelta(seconds=echonet_node.config.get("scan_interval", 10)))
    async_add_entities([EchonetNodeSwitchSensor(coordinator, echonet_node, switch, entry.entry_id) for switch in switches.items() if switch[0] in set_mapping])
    # async_add_entities([EchonetNodeSwitchSensor(echonet_node, (epc, {}), entry.entry_id) for epc in set_mapping if epc not in switches and epc >= 0xA0])


class EchonetNodeSwitchSensor(CoordinatorEntity, SwitchEntity):
    """Representation of a Switch."""

    def __init__(self, coordinator: MyDataUpdateCoordinator, node: EchonetLiteDevice, switch_def, entry_id) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        (self._epc, self._def) = switch_def
        self._node = node
        self._entity_id = entry_id
        self._keep = None
        self._keep_update_time = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.device_info['identifiers']}-switch-{self._epc}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._def.get(CONF_NAME, f"{self.device_info['name']} {str(hex(self._epc)).upper()}")

    @property
    def is_on(self) -> bool:
        if self._keep is not None:
            return self._keep
        """Return the state of the sensor."""
        return self.coordinator.get_prop(self._epc) == self._def.get("on")

    async def reset_keep(self, second, t):
        await asyncio.sleep(second)
        if t == self._keep_update_time:
            self._keep = None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._node.async_set_prop(self._epc, self._def.get("on"))
        if self._def.get("delay", 0) > 0:
            self._keep = True
            self._keep_update_time = datetime.datetime.now()
            asyncio.create_task(self.reset_keep(self._def.get("delay"), self._keep_update_time))
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._node.async_set_prop(self._epc, self._def.get("off"))
        if self._def.get("delay", 0) > 0:
            self._keep = False
            self._keep_update_time = datetime.datetime.now()
            asyncio.create_task(self.reset_keep(self._def.get("delay"), self._keep_update_time))
        self.async_write_ha_state()

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._def.get(CONF_DEVICE_CLASS, "switch")

    @property
    def icon(self):
        """Return the icon of this device."""
        return self._def.get(CONF_ICON)

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._node.device_info
