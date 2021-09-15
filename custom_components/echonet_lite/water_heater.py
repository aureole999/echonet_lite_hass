"""Support for Water Heater."""
from datetime import timedelta

from homeassistant.components.sensor import _LOGGER
from homeassistant.components.water_heater import WaterHeaterEntity, SUPPORT_TARGET_TEMPERATURE
from homeassistant.const import (
    ATTR_TEMPERATURE, TEMP_CELSIUS, PRECISION_WHOLE, CONF_FORCE_UPDATE,
)
from . import EchonetLiteDevice
from .const import DOMAIN
from .coordinator import MyDataUpdateCoordinator
from .echonet_lite_lib.device_type.water_heater import WaterHeater
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    echonet_node: EchonetLiteDevice = hass.data[DOMAIN].get(entry.entry_id)

    water_heater = echonet_node.config.get("water_heater")

    if water_heater:
        coordinator = await MyDataUpdateCoordinator.factory(entry.entry_id, hass, _LOGGER, "water_heater", update_interval=timedelta(seconds=echonet_node.config.get("scan_interval", 10)))
        async_add_entities([EchonetNodeWaterHeater(coordinator, echonet_node, water_heater, entry.entry_id)])


class EchonetNodeWaterHeater(CoordinatorEntity, WaterHeaterEntity):

    def __init__(self, coordinator: MyDataUpdateCoordinator, node: WaterHeater, config, entry_id) -> None:
        # def __init__(self, node: EchonetLiteDevice, sensor_def, entry_id) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        """Initialize the sensor."""
        self._node: WaterHeater = node
        self._conf = config
        self._entity_id = entry_id

        set_mapping = node.set_mapping
        self._attr_supported_features = config.get("supported_features")

        if 0xD1 not in set_mapping:
            self._attr_supported_features &= ~SUPPORT_TARGET_TEMPERATURE

        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_min_temp = config.get("min_temp")
        self._attr_max_temp = config.get("max_temp")
        self._attr_operation_list = ["Bath Auto", "Off"]
        self._attr_current_operation = "Bath Auto" if self._node.get_bath_auto_mode() else "Off"
        self._precision = PRECISION_WHOLE

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.device_info['identifiers']}-water-heater"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.device_info['name']} Water Heater"

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._node.device_info

    async def async_set_temperature(self, **kwargs):
        await self._node.set_temperature(kwargs.get(ATTR_TEMPERATURE))
        await self.async_update_ha_state()
        pass

    async def async_set_operation_mode(self, operation_mode):
        self._attr_current_operation = operation_mode
        await self._node.set_bath_auto_mode(operation_mode == "Bath Auto")
        await self.async_update_ha_state()

    pass

    async def async_turn_away_mode_on(self):
        pass

    async def async_turn_away_mode_off(self):
        pass

    def _handle_coordinator_update(self) -> None:
        self._attr_target_temperature = self._node.get_temperature()
        self._attr_current_operation = "Bath Auto" if self._node.get_bath_auto_mode() else "Off"
        self.async_write_ha_state()

    @property
    def force_update(self) -> bool:
        """We should force updates. Repeated states have meaning."""
        return self._conf.get(CONF_FORCE_UPDATE, False)
