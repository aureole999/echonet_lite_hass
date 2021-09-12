"""Support for Echonet lite binary sensors."""
from datetime import timedelta
from typing import cast

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity, CONF_STATE_CLASS, _LOGGER
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.custom_components.echonet_lite import EchonetLiteDevice
from homeassistant.custom_components.echonet_lite.const import DOMAIN
from homeassistant.custom_components.echonet_lite.coordinator import MyDataUpdateCoordinator
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

SCAN_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(hass, entry, async_add_entities):
    echonet_node: EchonetLiteDevice = hass.data[DOMAIN].get(entry.entry_id)

    get_mapping = echonet_node.get_mapping
    sensors = echonet_node.config.get("binary_sensors", {})
    coordinator = await MyDataUpdateCoordinator.factory(entry.entry_id, hass, _LOGGER, "binary_sensor", update_interval=timedelta(seconds=echonet_node.config.get("scan_interval", 10)))
    async_add_entities([EchonetNodeBinarySensor(coordinator, echonet_node, sensor, entry.entry_id) for sensor in sensors.items() if sensor[0] in get_mapping])


class EchonetNodeBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator: MyDataUpdateCoordinator, node: EchonetLiteDevice, sensor_def, entry_id) -> None:
        # def __init__(self, node: EchonetLiteDevice, sensor_def, entry_id) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        """Initialize the sensor."""
        self._node = node
        self._epc, self._data = sensor_def
        self._entity_id = entry_id

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.device_info['identifiers']}-binary-{self._epc}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.device_info['name']} {self._data.get(CONF_NAME, str(hex(self._epc)).upper())}"

    @property
    def is_on(self):
        return self.coordinator.get_prop(self._epc) == self._data.get("on")

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._data.get(CONF_DEVICE_CLASS)

    @property
    def icon(self):
        """Return the icon of this device."""
        return self._data.get(CONF_ICON)

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._node.device_info
