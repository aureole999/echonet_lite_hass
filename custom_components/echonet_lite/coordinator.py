import asyncio
import logging
from datetime import timedelta
from typing import Any, Callable, Awaitable, Optional

from homeassistant.core import HomeAssistant
from .const import DOMAIN
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, T


class MyDataUpdateCoordinator(DataUpdateCoordinator):
    instances: [Any, Any] = {}
    lock = asyncio.Lock()

    @staticmethod
    async def factory(entry_id, hass, _LOGGER, name, update_interval):

        async with MyDataUpdateCoordinator.lock:
            echonet_node = hass.data[DOMAIN].get(entry_id)
            if entry_id in MyDataUpdateCoordinator.instances:
                if echonet_node == MyDataUpdateCoordinator.instances[entry_id].node:
                    return MyDataUpdateCoordinator.instances[entry_id]

            async def async_update_data():
                await echonet_node.async_update()
                return echonet_node.props

            _LOGGER.debug(f"Create new coordinator for {entry_id}")
            c = MyDataUpdateCoordinator(
                hass,
                _LOGGER,
                # Name of the data. For logging purposes.
                name=name,
                update_method=async_update_data,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=update_interval,
                node=echonet_node
            )

            await c.async_config_entry_first_refresh()
            MyDataUpdateCoordinator.instances[entry_id] = c
        return c

    def get_prop(self, prop, t=int):
        return self.node.get_prop(prop, t)

    def __init__(self, hass: HomeAssistant, logger: logging.Logger, *, name: str, update_interval: Optional[timedelta] = None, update_method: Optional[Callable[[], Awaitable[T]]] = None, request_refresh_debouncer: Optional[Debouncer] = None,
                 node=None) -> None:
        super().__init__(hass, logger, name=name, update_interval=update_interval, update_method=update_method, request_refresh_debouncer=request_refresh_debouncer)
        self.node = node
