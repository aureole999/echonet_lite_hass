from enum import Enum

from homeassistant.custom_components.echonet_lite import EchonetLiteDevice
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.frame import Property


class Climate(EchonetLiteDevice):

    def __init__(self, identifier, host, gc, cc, ic, config: dict):
        super().__init__(identifier, host, gc, cc, ic, config)
        self._min_temp = config.get("climate").get("min_temp", 20)
        self._max_temp = config.get("climate").get("max_temp", 35)

    class FanMode(Enum):
        AUTO = 0x41
        LEVEL_1 = 0x31
        LEVEL_2 = 0x32
        LEVEL_3 = 0x33
        LEVEL_4 = 0x34
        LEVEL_5 = 0x35
        LEVEL_6 = 0x36
        LEVEL_7 = 0x37
        LEVEL_8 = 0x38

    class OperationMode(Enum):
        AUTO = 0x41
        COOL = 0x42
        HEAT = 0x43
        DRY = 0x44
        FAN = 0x45
        OTHER = 0x40

    class PowerSavingMode(Enum):
        ON = 0x41
        OFF = 0x42

    class PropKey(Enum):
        POWER = 0x80
        POWER_SAVING_MODE = 0x8F
        OPERATION_MODE = 0xB0
        AUTO_TEMP_CONTROL = 0XB1
        SPEED_SILENT_MODE = 0xB2
        SET_TEMP = 0xB3
        SET_HUMID = 0xB4
        SET_COOL_TEMP = 0xB5
        SET_HEAT_TEMP = 0xB6
        SET_DRY_TEMP = 0xB7
        POWER_CONSUMPTION = 0xB8
        CURRENT = 0xB9
        INDOOR_HUMID = 0xBA
        INDOOR_TEMP = 0xBB
        SET_USER_REMOTE_TEMP = 0xBC
        COOL_AIR_TEMP = 0xBD
        OUTDOOR_TEMP = 0xBE
        SET_RELATIVE_TEMP = 0xBF
        SET_FAN = 0xA0
        SET_AUTO_DIRECTION = 0xA1
        SET_SWING = 0xA3
        SET_WIND_VERTICAL = 0xA4
        SET_WIND_HORIZON = 0xA5
        SPECIAL_STATE = 0xAA
        NON_PRIORITY_STATE = 0xAB
        VENTILATION = 0xC0
        HUMIDIFIER = 0xC1
        VENTILATION_WIND = 0xC2
        HUMIDIFIER_LEVEL = 0xC4
        AIR_CLEAN_SUPPORT = 0xC6
        SET_AIR_CLEAN_FUNC = 0xC7
        AIR_REFRESH_SUPPORT = 0xC8
        SET_AIR_REFRESH = 0xC9
        SELF_CLEAN_SUPPORT = 0xCA
        SET_SELF_CLEAN = 0xCB
        SPECIAL_FUNC = 0xCC
        COMPONENT_STATUS = 0xCD
        SET_AIR_CLEAN = 0xCF

    def is_support(self, mode):
        return mode.value in self.set_mapping

    async def async_set_fan_mode(self, fan_mode: FanMode):
        await self.async_set_prop(Climate.PropKey.SET_FAN.value, fan_mode.value)

    async def async_set_power_saving_mode(self, on):
        await self.async_set_prop(Climate.PropKey.POWER_SAVING_MODE.value, 0x41 if on else 0x42)

    async def async_set_operation_mode(self, mode: OperationMode):
        if not mode:
            await self.async_set_prop(Climate.PropKey.POWER.value, 0x31)
            return
        await self.async_set_props([(Climate.PropKey.POWER.value, 0x30),
                                    (Climate.PropKey.OPERATION_MODE.value, mode.value)])

    def get_operation_mode(self):
        if self.get_prop(Climate.PropKey.POWER.value) == 0x31:
            return None
        return Climate.OperationMode(self.get_prop(Climate.PropKey.OPERATION_MODE.value))

    def get_fan_mode(self):
        return Climate.FanMode(self.get_prop(Climate.PropKey.SET_FAN.value))

    def get_power_saving_mode(self):
        return Climate.PowerSavingMode(self.get_prop(Climate.PropKey.POWER_SAVING_MODE.value))
