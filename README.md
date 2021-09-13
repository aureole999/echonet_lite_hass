# ECHONET Lite Integration for Home Assistant


A Home Assistant integration for ECHONET Lite compatible devices.

### Note
Only implement and test for my own devices:
- Toshiba HVAC
- Panasonic fuel cell Ene-farm (エネファーム) with Tokyo gas floor heater
- AIPHONE doorbell

Other brands HVAC system or devices might be work with this component.  
If it isn't, you can define your device in `echonet_lite_lib/device.py`

No test code and no separated library for now because I'm not familiar with Python.

__I am not responsible for any damage to the equipment caused by the use of this component__


## Installation
### Manual
Place the `custom_components` folder in your configuration directory

### HACS
Add this repository as a custom repository in HACS, see below for more information.
https://hacs.xyz/docs/faq/custom_repositories/

## Setup
1. Add integration from Home Assistant UI.
2. Find `Echonet Lite` in the integration list.
3. It will auto list all your ECHONET Lite compatible devices.<br><br> 
If there is nothing in the device list, please ensure ECHONET Lite protocol is enabled in your device and ensure your device and home assistant are in the same local network.<br><br>
This component needs to open UDP port `3000` for receiving ECHONET Lite package. Check your firewall if anything goes wrong.


4. Select one device to finish setup. Devices and entities will be available in the HA once you have done setup.
