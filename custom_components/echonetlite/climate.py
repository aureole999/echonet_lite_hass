from datetime import timedelta

from homeassistant.components.climate import ClimateEntity, _LOGGER, ATTR_MIN_TEMP, ATTR_MAX_TEMP
from homeassistant.components.climate.const import HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, \
    HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, ATTR_TARGET_TEMP_STEP, ATTR_FAN_MODES, PRESET_AWAY, PRESET_HOME, \
    ClimateEntityFeature
from homeassistant.components.generic_thermostat.climate import CONF_PRECISION
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT, ATTR_TEMPERATURE, ATTR_SUPPORTED_FEATURES, TEMP_CELSIUS, \
    PRECISION_WHOLE, CONF_FORCE_UPDATE
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyDataUpdateCoordinator
from .echonet_lite_lib.device_type.climate import Climate
from .helper import get_key


async def async_setup_entry(hass, entry, async_add_entities):
    echonet_node = hass.data[DOMAIN].get(entry.entry_id)

    climate = echonet_node.config.get("climate")

    if climate:
        coordinator = await MyDataUpdateCoordinator.factory(entry.entry_id, hass, _LOGGER, "climate", update_interval=timedelta(seconds=echonet_node.config.get("scan_interval", 10)))
        async_add_entities([EchonetLiteClimate(coordinator, echonet_node, climate, entry.entry_id)], True)


class EchonetLiteClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Mitsubishi ECHONET climate device."""

    HVAC_MODE = {
        HVAC_MODE_OFF: None,
        HVAC_MODE_HEAT: Climate.OperationMode.HEAT,
        HVAC_MODE_COOL: Climate.OperationMode.COOL,
        HVAC_MODE_AUTO: Climate.OperationMode.AUTO,
        HVAC_MODE_DRY: Climate.OperationMode.DRY,
        HVAC_MODE_FAN_ONLY: Climate.OperationMode.FAN,
    }

    PRESET_MODE = {
        PRESET_AWAY: Climate.PowerSavingMode.ON,
        PRESET_HOME: Climate.PowerSavingMode.OFF
    }

    def __init__(self, coordinator: MyDataUpdateCoordinator, node: Climate, config, entry_id):
        """Initialize the climate device."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._entity_id = entry_id
        self._node = node
        self._attr_temperature_unit = config.get(CONF_UNIT_OF_MEASUREMENT, TEMP_CELSIUS)
        self._attr_precision = config.get(CONF_PRECISION, PRECISION_WHOLE)
        self._attr_target_temperature_step = config.get(ATTR_TARGET_TEMP_STEP, PRECISION_WHOLE)
        self._attr_supported_features = config.get(ATTR_SUPPORTED_FEATURES)
        self._attr_min_temp = config.get(ATTR_MIN_TEMP, 0)
        self._attr_max_temp = config.get(ATTR_MAX_TEMP, 50)
        self._attr_hvac_modes = [m for m in config.get("hvac_modes", []) if m in EchonetLiteClimate.HVAC_MODE]
        self._force_update = config.get(CONF_FORCE_UPDATE, False)

        if not self._node.is_support(Climate.PropKey.SET_TEMP):
            self._attr_supported_features &= ~ClimateEntityFeature.TARGET_TEMPERATURE

        if not self._node.is_support(Climate.PropKey.SET_HUMID):
            self._attr_supported_features &= ~ClimateEntityFeature.TARGET_HUMIDITY

        if not self._node.is_support(Climate.PropKey.SET_FAN) or len(config.get(ATTR_FAN_MODES, [])) == 0:
            self._attr_supported_features &= ~ClimateEntityFeature.FAN_MODE
        else:
            self._attr_fan_modes = config.get(ATTR_FAN_MODES, [])
            self._fan_modes_mapping = dict(zip(self._attr_fan_modes, [e for e in Climate.FanMode]))

        if self._node.is_support(Climate.PropKey.POWER_SAVING_MODE):
            self._attr_supported_features &= ~ClimateEntityFeature.PRESET_MODE
        else:
            self._attr_preset_modes = list(EchonetLiteClimate.PRESET_MODE.keys())

        if not self._node.is_support(Climate.PropKey.SET_SWING):
            self._attr_supported_features &= ~ClimateEntityFeature.SWING_MODE

        self.refresh_current_status()

    async def async_set_temperature(self, **kwargs) -> None:
        self._attr_target_temperature = int(kwargs.get(ATTR_TEMPERATURE))
        await self._node.async_set_prop(Climate.PropKey.SET_TEMP.value, self._attr_target_temperature)
        await self.async_update_ha_state()

    async def async_set_humidity(self, humidity: int) -> None:
        self._attr_target_humidity = humidity
        await self._node.async_set_prop(Climate.PropKey.SET_HUMID.value, humidity)
        await self.async_update_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        self._attr_fan_mode = fan_mode
        await self._node.async_set_fan_mode(self._fan_modes_mapping.get(fan_mode))
        await self.async_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        self._attr_hvac_mode = hvac_mode
        await self._node.async_set_operation_mode(EchonetLiteClimate.HVAC_MODE.get(hvac_mode))
        await self.async_update_ha_state()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        pass

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == PRESET_AWAY:
            await self._node.async_set_power_saving_mode(True)
        else:
            await self._node.async_set_power_saving_mode(False)
        await self.async_update_ha_state()

    async def async_turn_aux_heat_on(self) -> None:
        pass

    async def async_turn_aux_heat_off(self) -> None:
        pass

    def refresh_current_status(self):
        self._attr_target_temperature = self._node.get_prop(Climate.PropKey.SET_TEMP.value)
        self._attr_target_humidity = self._node.get_prop(Climate.PropKey.SET_HUMID.value)
        self._attr_current_temperature = self._node.get_prop(Climate.PropKey.INDOOR_TEMP.value)
        self._attr_current_humidity = self._node.get_prop(Climate.PropKey.INDOOR_HUMID.value)
        self._attr_hvac_mode = get_key(EchonetLiteClimate.HVAC_MODE, self._node.get_operation_mode())
        self._attr_fan_mode = get_key(self._fan_modes_mapping, self._node.get_fan_mode())
        self._attr_preset_mode = get_key(EchonetLiteClimate.PRESET_MODE, self._node.get_fan_mode())

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._node.device_info

    @property
    def name(self):
        """Return the name of the device."""
        return f"{self.device_info['name']}"

    def _handle_coordinator_update(self) -> None:
        self.refresh_current_status()
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.device_info['identifiers']}-climate"

    @property
    def force_update(self) -> bool:
        """We should force updates. Repeated states have meaning."""
        return self._force_update
