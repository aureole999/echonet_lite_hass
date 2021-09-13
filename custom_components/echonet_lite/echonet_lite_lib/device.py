from functools import reduce

from homeassistant.components.binary_sensor import DEVICE_CLASS_OCCUPANCY
from homeassistant.components.climate import HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, ATTR_TARGET_TEMP_STEP, ATTR_MIN_TEMP, ATTR_HVAC_MODES
from homeassistant.components.climate.const import HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, ATTR_MAX_TEMP, SUPPORT_TARGET_HUMIDITY, SUPPORT_FAN_MODE, ATTR_FAN_MODES, FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, SUPPORT_PRESET_MODE, SUPPORT_SWING_MODE
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING
from homeassistant.components.water_heater import SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE
from ..const import CONF_STATE_CLASS
from homeassistant.const import DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, DEVICE_CLASS_POWER, POWER_WATT, \
    DEVICE_CLASS_ENERGY, ENERGY_WATT_HOUR, DEVICE_CLASS_GAS, VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR, \
    VOLUME_CUBIC_METERS, VOLUME_LITERS, CONF_DEVICE_CLASS, CONF_UNIT_OF_MEASUREMENT, DEVICE_CLASS_CURRENT, ELECTRIC_CURRENT_AMPERE, DEVICE_CLASS_HUMIDITY, PERCENTAGE, ATTR_SUPPORTED_FEATURES, PRECISION_WHOLE

DEVICE_SPEC = {
    0x00: {
        0x08: {
            "class_name": "GenericDevice",
            "binary_sensors": {
                0xB1: {"name": "Visitor detection", CONF_DEVICE_CLASS: DEVICE_CLASS_OCCUPANCY, "on": 0x41},
            }
        }
    },
    0x01: {
        0x30: {
            "class_name": "Climate",
            "sensors": {
                0xB9: {"name": "Current consumption", CONF_DEVICE_CLASS: DEVICE_CLASS_CURRENT, CONF_UNIT_OF_MEASUREMENT: ELECTRIC_CURRENT_AMPERE},
                0xBA: {"name": "Indoor relative humidity", CONF_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY, CONF_UNIT_OF_MEASUREMENT: PERCENTAGE},
                0xBB: {"name": "Indoor temperature", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
                0xBC: {"name": "Remote controller temperature", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
                0xBD: {"name": "Cooled air temperature", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
                0xBE: {"name": "Outdoor temperature", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
            },
            "climate": {
                ATTR_HVAC_MODES: [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY],
                ATTR_MIN_TEMP: 16,
                ATTR_MAX_TEMP: 30,
                ATTR_TARGET_TEMP_STEP: PRECISION_WHOLE,
                ATTR_SUPPORTED_FEATURES: SUPPORT_TARGET_TEMPERATURE | SUPPORT_TARGET_HUMIDITY | SUPPORT_FAN_MODE | SUPPORT_PRESET_MODE | SUPPORT_SWING_MODE,
                ATTR_FAN_MODES: [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
            },
            "switches": {
                0x8F: {"name": "Power saving", "on": 0x41, "off": 0x42},
                0xCF: {"name": "Air purifier", "on": 0x41, "off": 0x42},
            },

            # Toshiba Climate
            0x69: {
                "class_name": "ToshibaClimate",
                "climate": {
                    ATTR_FAN_MODES: [FAN_AUTO, "silent", FAN_LOW, "medium low", FAN_MEDIUM, "medium high", FAN_HIGH, "powerful"]
                },
            }
        }
    },
    0x02: {
        0x7C: {  # Fuel Cell
            "class_name": "GenericDevice",
            "sensors": {
                0xC1: {"name": "Temperature of water in water heater", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
                0xC2: {"name": "Rated power generation output", CONF_DEVICE_CLASS: DEVICE_CLASS_POWER, CONF_UNIT_OF_MEASUREMENT: POWER_WATT},
                0xC3: {"name": "Heating value of hot water storage tank", CONF_DEVICE_CLASS: None, CONF_UNIT_OF_MEASUREMENT: "MJ"},
                0xC4: {"name": "Instantaneous power generation output", CONF_DEVICE_CLASS: DEVICE_CLASS_POWER, CONF_UNIT_OF_MEASUREMENT: POWER_WATT},
                0xC5: {"name": "Cumulative power generation output", CONF_DEVICE_CLASS: DEVICE_CLASS_ENERGY, CONF_UNIT_OF_MEASUREMENT: ENERGY_WATT_HOUR, CONF_STATE_CLASS: STATE_CLASS_TOTAL_INCREASING},
                0xC7: {"name": "Instantaneous gas consumption", CONF_DEVICE_CLASS: DEVICE_CLASS_GAS, CONF_UNIT_OF_MEASUREMENT: VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR, "scale": 0.001},
                0xC8: {"name": "Cumulative gas consumption", CONF_DEVICE_CLASS: DEVICE_CLASS_GAS, CONF_UNIT_OF_MEASUREMENT: VOLUME_CUBIC_METERS, "scale": 0.001, CONF_STATE_CLASS: STATE_CLASS_TOTAL_INCREASING},
                0xCB: {"name": "Power generation status", CONF_DEVICE_CLASS: None, "enum": {0x41: "Generating", 0x42: "Stopped", 0x43: "Starting", 0x44: "Stopping", 0x45: "Idling"}},
                0xCC: {"name": "In-house instantaneous power consumption", CONF_DEVICE_CLASS: DEVICE_CLASS_POWER, CONF_UNIT_OF_MEASUREMENT: POWER_WATT},
                0xCD: {"name": "In-house cumulative power consumption", CONF_DEVICE_CLASS: DEVICE_CLASS_ENERGY, CONF_UNIT_OF_MEASUREMENT: ENERGY_WATT_HOUR, CONF_STATE_CLASS: STATE_CLASS_TOTAL_INCREASING},
                0xE1: {"name": "Remaining hot water amount", CONF_DEVICE_CLASS: None, CONF_UNIT_OF_MEASUREMENT: VOLUME_LITERS},
                0xE2: {"name": "Tank capacity", CONF_DEVICE_CLASS: None, CONF_UNIT_OF_MEASUREMENT: VOLUME_LITERS},
            },
            "binary_sensors": {
                0x80: {"name": "Operation status", "on": 0x30},
            },
            "switches": {
                0xCA: {"name": "Power generation setting", "on": 0x41, "off": 0x42}
            },

            # Panasonic Fuel Cell
            0x0B: {
                'FC-70JR13T': {
                    "scan_interval": 5,
                    "sensors": {
                        0xF2: {"name": "Hot water used today", CONF_DEVICE_CLASS: None, CONF_UNIT_OF_MEASUREMENT: VOLUME_LITERS},
                        0xF4: {"name": "Hot water level in tank"},
                        0xF6: {"name": "Cumulative hot water consumption", CONF_UNIT_OF_MEASUREMENT: VOLUME_LITERS, "scale": 0.01},
                    }
                }
            }
        },

        0x72: {
            "class_name": "WaterHeater",
            "sensors": {
                0xE1: {"name": "Bath temperature", CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE, CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS},
                0xF0: {},
            },
            "binary_sensors": {
                0xD0: {"name": "Hot water heating status", "on": 0x41},
                0xE2: {"name": "Bath water heating status", "on": 0x41},
            },
            "water_heater": {
                ATTR_SUPPORTED_FEATURES: SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE,
                ATTR_MIN_TEMP: 32,
                ATTR_MAX_TEMP: 60
            }
        },
    },
    # AV Related Device
    0x06: {
        # Display
        0x01: {
            "class_name": "Display",
            "services": {
                0xB3: {"name": "display_notify", "func": "async_notify"},
            },
        },
    },

    # User Define Group
    0x0F: {
        0x70: {
            "class_name": "GenericDevice",

            # Panasonic
            0x0B: {
                "sensors": {
                    0xE1: {"name": ""}
                },
                "switches": {
                    0x80: {"name": "power", "on": 0x30, "off": 0x31, "delay": 20}
                }
            },
        },
    },
}


def get_config(gc, cc, manufacturer=None, model=None):
    res = merge(DEVICE_SPEC.get(gc, {}), DEVICE_SPEC.get(gc, {}).get(cc), cc)
    if manufacturer:
        res = merge(res, DEVICE_SPEC.get(gc, {}).get(cc, {}).get(manufacturer), manufacturer)
    if model:
        res = merge(res, DEVICE_SPEC.get(gc, {}).get(cc, {}).get(manufacturer, {}).get(model), model)
    return res


def merge_dicts(dict1, dict2, include=None):
    for k in set(dict1.keys()).union(dict2.keys()):
        if include is not None and k not in include:
            continue
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield k, dict(merge_dicts(dict1[k], dict2[k]))
            else:
                yield k, dict2[k]
        else:
            if k in dict1:
                yield k, dict1[k]
            else:
                yield k, dict2[k]


def merge(dict1, dict2, include=None):
    if dict1 is None:
        return dict2
    if dict2 is None:
        return dict1
    return dict(merge_dicts(dict1, dict2, {"class_name", "scan_interval", "services", "switches", "sensors", "climate", "water_heater", "binary_sensors", "services"}))
