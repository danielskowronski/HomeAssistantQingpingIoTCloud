"""Interfaces with the Integration 101 Template api sensors."""

import math
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

#from .api import Device, DeviceType
from qingping_iot_cloud import QingpingCloud, QingpingDevice, QingpingDeviceProperty
from .const import DOMAIN
from .coordinator import QingpingCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: QingpingCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    sensors = [
        #QingpingSensor(coordinator, device)
        #for device in coordinator.data.devices
    ]
    for device in coordinator.data.devices:
        # FIXME: read device properties live or from config flow
        # official sensor matrix is incorrect -> https://developer.qingping.co/cloud-to-cloud/specification-guidelines#2-products-list-and-support-note
        # since it's unlikely data frame from given device changes (i.e. device always sends same parameters) 
        # it's safe enough to assume that what's visible for given device at integration launch is always going to correct
        # if not - we can just reload the integration
        for property in device.data.keys():
            sensors.append(QingpingSensor(coordinator, device, property))
        #sensors.append(QingpingSensor(coordinator, device, "battery"))
        #sensors.append(QingpingSensor(coordinator, device, "signal"))
        #sensors.append(QingpingSensor(coordinator, device, "temperature"))
        #sensors.append(QingpingSensor(coordinator, device, "humidity"))
        #sensors.append(QingpingSensor(coordinator, device, "co2"))

    # Create the sensors.
    async_add_entities(sensors)


class QingpingSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: QingpingCoordinator, device: QingpingDevice, attribute: str) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_mac = device.mac
        self.device_mac_formatted = (":".join(self.device_mac[i:i+2] for i in range(0, len(self.device_mac), 2))).upper()
        self.attribute = attribute
        
        self._parse_values()
        
    def _parse_values(self) -> None:
        self._raw_value = self.device.get_property(self.attribute).get_ha_value()
        self._is_available = self._raw_value is not None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_mac(
            self.device_mac
        )
        self._parse_values()
        _LOGGER.debug("Device: %s", self.device)
        #_LOGGER.warning(f"_handle_coordinator_update: {self.device_mac_formatted}")
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        # FIXME: support proper device classes
        ha_class = self.device.get_property(self.attribute).get_ha_class()
        if ha_class is None:
            return None
        else:
            return SensorDeviceClass(ha_class)
        #if self.attribute == "battery":
        #    return SensorDeviceClass.BATTERY
        #if self.attribute == "signal":
        #    return SensorDeviceClass.SIGNAL_STRENGTH
        #if self.attribute == "temperature":
        #    return SensorDeviceClass.TEMPERATURE
        #if self.attribute == "humidity":
        #    return SensorDeviceClass.HUMIDITY
        #if self.attribute == "co2":
        #    return SensorDeviceClass.CO2
    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        return DeviceInfo(
            #name=f"Qingping_{self.device_mac}_{self.attribute}",
            name=f"{self.device.name}",
            manufacturer="Qingping",
            model=self.device.product_en_name,
            sw_version=self.device.version,
            identifiers={
                (
                    DOMAIN,
                    f"{self.coordinator.data.controller_name}-{self.device.mac}-{self.attribute}",
                )
            },
            connections={("mac", self.device_mac_formatted)},
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.device.name} {self.device.get_property(self.attribute).get_ha_title()}"

    @property
    def available(self):
        # Indicate whether the entity is available
        return self._is_available

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        #return float(self.device.state)
        return STATE_UNAVAILABLE if not self._is_available else self._raw_value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        #return UnitOfTemperature.CELSIUS
        # TODO: support all options from QingpingDeviceProperty.DEV_PROP_SPEC, sync values
        return self.device.get_property(self.attribute).get_unit()
        #if self.attribute == "battery":
        #    return PERCENTAGE
        #if self.attribute == "signal":
        #    return SIGNAL_STRENGTH_DECIBELS_MILLIWATT
        #if self.attribute == "temperature":
        #    return UnitOfTemperature.CELSIUS
        #if self.attribute == "humidity":
        #    return PERCENTAGE
        #if self.attribute == "co2":
        #    return CONCENTRATION_PARTS_PER_MILLION

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.mac}-{self.attribute}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["timestamp"] = self.device.get_property("timestamp").value
        attrs["nickname"] = self.device.name
        attrs["offline"] = self.device.status_offline
        attrs["setting_report_interval"] = self.device.setting_report_interval
        attrs["setting_collect_interval"] = self.device.setting_collect_interval
        return attrs

# TODO: add binary sensor to check if device is considered offline