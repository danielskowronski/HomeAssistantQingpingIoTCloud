"""Qingping IoT Cloud integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from qingping_iot_cloud import QingpingCloud, QingpingDevice, QingpingDeviceProperty
from qingping_iot_cloud.QingpingCloud import APIAuthError, APIConnectionError
from .const import DEFAULT_SCAN_INTERVAL, HTTP_GET_TIMEOUT

_LOGGER = logging.getLogger(__name__)


@dataclass
class QingpingAPIData:
    """Class to hold api data."""

    controller_name: str
    devices: list[QingpingDevice]


class QingpingCoordinator(DataUpdateCoordinator):
    """My Qingping coordinator."""

    data: QingpingAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.app_key = config_entry.data[CONF_CLIENT_ID]
        self.app_secret = config_entry.data[CONF_CLIENT_SECRET]

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here
        self.cloud = QingpingCloud(app_key=self.app_key, app_secret=self.app_secret)
    
    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.debug("Starting QingpingCoordinator.async_update_data")
        try:
            await asyncio.wait_for(self.hass.async_add_executor_job(self.cloud.connect), HTTP_GET_TIMEOUT)
            devices = await asyncio.wait_for(self.hass.async_add_executor_job(self.cloud.get_devices), HTTP_GET_TIMEOUT)
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            _LOGGER.error(err)
            #_LOGGER.debug(f"Failed to update devices ({err}), marking them as unavailable immediately")
            #return QingpingAPIData(self.cloud.API_URL_PREFIX, [])
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return QingpingAPIData(self.cloud.API_URL_PREFIX, devices)

    def get_device_by_mac(
        self, device_mac: int
    ) -> QingpingDevice.QingpingDevice | None:
        """Return device by device MAC."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            return [
                device
                for device in self.data.devices
                if device.mac == device_mac
            ][0]
        except IndexError:
            return None
