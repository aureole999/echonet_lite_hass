import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE
from homeassistant.custom_components.echonet_lite.const import DOMAIN
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.EchonetLiteNodes import EchonetLiteDevice
from homeassistant.custom_components.echonet_lite.echonet_lite_lib.eojx import GROUP_NAME, CLASS_NAME
from homeassistant.data_entry_flow import FlowResult


# config_entry_flow.register_discovery_flow(
#     DOMAIN,
#     "Echonet Lite Node",
#     async_get_discoverable_devices,
# )

class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None) -> FlowResult:
        return await self.async_step_pick_device(user_input)

    async def async_step_pick_device(self, user_input=None) -> FlowResult:
        if not user_input:
            discovered_node = await EchonetLiteDevice.discovery()
            devices_name = dict(zip(("{}_{}_{}_{}_{}".format(i.host, i.gc, i.cc, i.ic, i.identifier) for i in discovered_node),
                                    ("{} {} ({})".format(CLASS_NAME.get(i.gc, {}).get(i.cc, f"{GROUP_NAME.get(i.gc, i.gc)} {i.cc}"), i.ic, i.host) for i in discovered_node)))
            return self.async_show_form(
                step_id="pick_device",
                data_schema=vol.Schema({vol.Required(CONF_DEVICE): vol.In(devices_name)}),
            )

        selected: str = user_input["device"]

        host, gc, cc, ic, identifier = selected.split("_")
        gc, cc, ic = int(gc), int(cc), int(ic)
        if not self.unique_id:
            await self.async_set_unique_id(f'{identifier}_{gc}_{cc}_{ic}')
            self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="{} {} ({})".format(CLASS_NAME.get(gc, {}).get(cc, f"{GROUP_NAME.get(gc, gc)} {cc}"), ic, host),
            data={
                "identifier": identifier,
                "gc": gc,
                "cc": cc,
                "ic": ic
            }
        )
