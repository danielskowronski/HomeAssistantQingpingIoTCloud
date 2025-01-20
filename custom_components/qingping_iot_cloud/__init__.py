"""The Qingping IoT Cloud integration."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .coordinator import QingpingCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator
    cancel_update_listener: Callable


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Qingping IoT Cloud Integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = QingpingCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.cloud.is_connected():
        raise ConfigEntryNotReady

    cancel_update_listener = config_entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = RuntimeData(
        coordinator, cancel_update_listener
    )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def _async_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle config options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry  # noqa: ARG001
) -> bool:
    """Delete device if selected from UI."""
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN][config_entry.entry_id].cancel_update_listener()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
