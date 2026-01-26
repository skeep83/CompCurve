"""Sensor platform for Heat Demand integration."""
from __future__ import annotations

import logging
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_CLIMATE_ENTITIES, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Heat Demand sensor."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HeatDemandSensor(coordinator)])


class HeatDemandCoordinator:
    """Coordinator to manage data updates for the sensor."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.config_entry = config_entry
        self.data: dict = {}
        self._unsub_tracker = None
        self._listeners: list[Callable[[], None]] = []

        self.climate_entities: list[str] = config_entry.data.get(
            CONF_CLIMATE_ENTITIES, []
        )

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": "Heat Demand",
            "manufacturer": "Heat Demand",
            "model": "Radiator Heat Demand Calculator",
        }

    def add_listener(self, update_callback: Callable[[], None]) -> Callable[[], None]:
        """Add a listener for data updates."""
        self._listeners.append(update_callback)

        def remove_listener():
            self._listeners.remove(update_callback)

        return remove_listener

    async def async_refresh(self) -> None:
        """Refresh data from source sensors."""
        self._update_data()

    def _update_data(self) -> None:
        """Calculate the maximum heat demand across all climate entities."""
        max_diff = 0.0
        individual_demands = {}

        for entity_id in self.climate_entities:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable"):
                continue

            target_temp = state.attributes.get("temperature")
            current_temp = state.attributes.get("current_temperature")

            if target_temp is None or current_temp is None:
                continue

            try:
                target = float(target_temp)
                current = float(current_temp)
                diff = target - current
                # Store individual demand (can be negative if room is too warm)
                individual_demands[entity_id] = round(diff, 1)
                # Track the maximum demand (clipped to >= 0)
                if diff > max_diff:
                    max_diff = diff
            except (ValueError, TypeError):
                continue

        # Clip the maximum demand to never fall below zero
        self.data = {
            "max_demand": round(max(0.0, max_diff), 1),
            "individual_demands": individual_demands,
        }

        _LOGGER.debug("Heat Demand data: %s", self.data)

    @callback
    def _async_source_changed(self, event) -> None:
        """Handle source entity state changes."""
        self._update_data()
        for listener in self._listeners:
            listener()

    async def async_start_tracking(self) -> None:
        """Start tracking source entities."""
        if self._unsub_tracker is not None:
            return

        if not self.climate_entities:
            return

        self._unsub_tracker = async_track_state_change_event(
            self.hass,
            self.climate_entities,
            self._async_source_changed,
        )

    async def async_stop_tracking(self) -> None:
        """Stop tracking source entities."""
        if self._unsub_tracker:
            self._unsub_tracker()
            self._unsub_tracker = None


class HeatDemandSensor(SensorEntity):
    """Sensor that shows the maximum heat demand across all radiators."""

    _attr_has_entity_name = True
    _attr_name = "Max Heat Demand"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:radiator"

    def __init__(self, coordinator: HeatDemandCoordinator) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_max_demand"
        self._remove_listener: Callable[[], None] | None = None

    @property
    def device_info(self):
        """Return device info."""
        return self._coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the maximum heat demand."""
        return self._coordinator.data.get("max_demand")

    @property
    def extra_state_attributes(self):
        """Return extra state attributes showing individual radiator demands."""
        attrs = {
            "climate_entities": self._coordinator.climate_entities,
        }
        individual = self._coordinator.data.get("individual_demands", {})
        if individual:
            attrs["individual_demands"] = individual
        return attrs

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await self._coordinator.async_start_tracking()
        self._remove_listener = self._coordinator.add_listener(
            self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is removed from hass."""
        if self._remove_listener:
            self._remove_listener()
        await self._coordinator.async_stop_tracking()
