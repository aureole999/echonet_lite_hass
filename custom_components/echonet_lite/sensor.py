"""Support for Daikin AC sensors."""
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, _LOGGER
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
)
from . import EchonetLiteDevice
from .const import DOMAIN, CONF_STATE_CLASS
from .coordinator import MyDataUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    echonet_node: EchonetLiteDevice = hass.data[DOMAIN].get(entry.entry_id)

    get_mapping = echonet_node.get_mapping
    sensors = echonet_node.config.get("sensors", {})
    coordinator = await MyDataUpdateCoordinator.factory(entry.entry_id, hass, _LOGGER, "sensor", update_interval=timedelta(seconds=echonet_node.config.get("scan_interval", 10)))
    async_add_entities([EchonetNodeSensor(coordinator, echonet_node, sensor, entry.entry_id) for sensor in sensors.items() if sensor[0] in get_mapping])
    # async_add_entities([EchonetNodeSensor(echonet_node, sensor, entry.entry_id) for sensor in sensors.items() if sensor[0] in get_mapping])
    async_add_entities([EchonetNodeSensor(coordinator, echonet_node, (epc, {}), entry.entry_id) for epc in get_mapping if epc not in sensors and epc >= 0xF0])
    # async_add_entities([EchonetNodeSensor(echonet_node, (epc, {}), entry.entry_id) for epc in get_mapping if epc not in sensors and epc >= 0xA0])


class EchonetNodeSensor(CoordinatorEntity, SensorEntity):
    # class EchonetNodeSensor(SensorEntity):
    """Representation of a Sensor."""

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
        return f"{self.device_info['identifiers']}-sensor-{self._epc}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.device_info['name']} {self._data.get(CONF_NAME, str(hex(self._epc)).upper())}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # return self._node.get_prop(self._epc) * self._data.get("scale", 1)
        if self._data.get("enum"):
            return self._data.get("enum").get(self.coordinator.get_prop(self._epc), f"Unknown state: {self.coordinator.get_prop(self._epc)}")
        v = self.coordinator.get_prop(self._epc)
        if type(v) == int or type(v) == float:
            return v * self._data.get("scale", 1)
        return v

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._data.get(CONF_DEVICE_CLASS)

    @property
    def icon(self):
        """Return the icon of this device."""
        return self._data.get(CONF_ICON)

    @property
    def state_class(self):
        """Return the state_class of this device."""
        return self._data.get(CONF_STATE_CLASS)

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._data.get(CONF_UNIT_OF_MEASUREMENT)

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._node.device_info
