"""Sensor platform for Compensation Curve integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_EXPONENT,
    CONF_HEAT_CURVE,
    CONF_HEAT_DEMAND_COEFFICIENT,
    CONF_HEAT_DEMAND_SENSOR,
    CONF_MAX_FLOW_TEMP,
    CONF_MIN_FLOW_TEMP,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_SCALE_FACTOR,
    CONF_BASE_TEMP,
    CONF_SOLAR_COEFFICIENT,
    CONF_SUNLIGHT_SENSOR,
    CONF_WIND_COEFFICIENT,
    CONF_WIND_EXPONENT,
    CONF_WIND_SPEED_SENSOR,
    DEFAULT_EXPONENT,
    DEFAULT_HEAT_CURVE,
    DEFAULT_HEAT_DEMAND_COEFFICIENT,
    DEFAULT_MAX_FLOW_TEMP,
    DEFAULT_MIN_FLOW_TEMP,
    DEFAULT_SCALE_FACTOR,
    DEFAULT_BASE_TEMP,
    DEFAULT_SOLAR_COEFFICIENT,
    DEFAULT_WIND_COEFFICIENT,
    DEFAULT_WIND_EXPONENT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CompCurveSensorEntityDescription(SensorEntityDescription):
    """Describes a CompCurve sensor entity."""

    value_fn: Callable[[dict], float | None] = lambda x: None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Compensation Curve sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[SensorEntity] = [
        CompCurveMainSensor(coordinator),
        CompCurveComponentSensor(
            coordinator,
            CompCurveSensorEntityDescription(
                key="compensated_flow_temp",
                name="Compensated Flow Temperature",
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                entity_category=EntityCategory.DIAGNOSTIC,
                value_fn=lambda d: d.get("compensated_temp"),
            ),
        ),
    ]

    # Only add wind adjustment sensor if wind sensor is configured
    if config_entry.data.get(CONF_WIND_SPEED_SENSOR):
        entities.append(
            CompCurveComponentSensor(
                coordinator,
                CompCurveSensorEntityDescription(
                    key="wind_adjustment",
                    name="Wind Adjustment",
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    icon="mdi:thermometer-plus",
                    entity_category=EntityCategory.DIAGNOSTIC,
                    value_fn=lambda d: d.get("wind_adjustment"),
                ),
            ),
        )

    # Only add solar adjustment sensor if sunlight sensor is configured
    if config_entry.data.get(CONF_SUNLIGHT_SENSOR):
        entities.append(
            CompCurveComponentSensor(
                coordinator,
                CompCurveSensorEntityDescription(
                    key="solar_adjustment",
                    name="Solar Adjustment",
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    icon="mdi:thermometer-minus",
                    entity_category=EntityCategory.DIAGNOSTIC,
                    value_fn=lambda d: d.get("solar_adjustment"),
                ),
            ),
        )

    # Only add heat demand adjustment sensor if heat demand sensor is configured
    if config_entry.data.get(CONF_HEAT_DEMAND_SENSOR):
        entities.append(
            CompCurveComponentSensor(
                coordinator,
                CompCurveSensorEntityDescription(
                    key="heat_demand_adjustment",
                    name="Heat Demand Adjustment",
                    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                    icon="mdi:radiator",
                    entity_category=EntityCategory.DIAGNOSTIC,
                    value_fn=lambda d: d.get("heat_demand_adjustment"),
                ),
            ),
        )

    async_add_entities(entities)


class CompCurveCoordinator:
    """Coordinator to manage data updates for all sensors."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.config_entry = config_entry
        self.data: dict = {}
        self._unsub_tracker = None
        self._listeners: list[Callable[[], None]] = []

        # Get configuration
        data = config_entry.data
        self.outdoor_sensor = data[CONF_OUTDOOR_TEMP_SENSOR]
        self.wind_sensor = data.get(CONF_WIND_SPEED_SENSOR, "")
        self.sunlight_sensor = data.get(CONF_SUNLIGHT_SENSOR, "")
        self.heat_demand_sensor = data.get(CONF_HEAT_DEMAND_SENSOR, "")

        # Get parameters with defaults
        self.heat_curve = data.get(CONF_HEAT_CURVE, DEFAULT_HEAT_CURVE)
        self.base_temp = data.get(CONF_BASE_TEMP, DEFAULT_BASE_TEMP)
        self.min_flow = data.get(CONF_MIN_FLOW_TEMP, DEFAULT_MIN_FLOW_TEMP)
        self.max_flow = data.get(CONF_MAX_FLOW_TEMP, DEFAULT_MAX_FLOW_TEMP)
        self.scale_factor = data.get(CONF_SCALE_FACTOR, DEFAULT_SCALE_FACTOR)
        self.exponent = data.get(CONF_EXPONENT, DEFAULT_EXPONENT)
        self.wind_coefficient = data.get(CONF_WIND_COEFFICIENT, DEFAULT_WIND_COEFFICIENT)
        self.wind_exponent = data.get(CONF_WIND_EXPONENT, DEFAULT_WIND_EXPONENT)
        self.solar_coefficient = data.get(CONF_SOLAR_COEFFICIENT, DEFAULT_SOLAR_COEFFICIENT)
        self.heat_demand_coefficient = data.get(CONF_HEAT_DEMAND_COEFFICIENT, DEFAULT_HEAT_DEMAND_COEFFICIENT)

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": "Compensation Curve",
            "manufacturer": "CompCurve",
            "model": "Weather Compensation Calculator",
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

    def _get_sensor_value(self, entity_id: str) -> float | None:
        """Get numeric value from a sensor entity."""
        if not entity_id:
            return None

        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return None

        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    def _update_data(self) -> None:
        """Calculate all values."""
        outdoor_temp = self._get_sensor_value(self.outdoor_sensor)

        if outdoor_temp is None:
            self.data = {}
            return

        wind_speed = self._get_sensor_value(self.wind_sensor) or 0
        sunlight = self._get_sensor_value(self.sunlight_sensor) or 0
        heat_demand = self._get_sensor_value(self.heat_demand_sensor) or 0

        # Calculate components
        temp_diff = max(0, self.base_temp - outdoor_temp)
        compensated_temp = self.scale_factor * (self.heat_curve * temp_diff) ** self.exponent + self.base_temp
        wind_adjustment = self.wind_coefficient * wind_speed ** self.wind_exponent
        solar_adjustment = self.solar_coefficient * sunlight
        heat_demand_adjustment = self.heat_demand_coefficient * heat_demand

        # Calculate final temperature
        flow_temp_raw = compensated_temp + wind_adjustment - solar_adjustment + heat_demand_adjustment
        flow_temp = min(self.max_flow, max(self.min_flow, flow_temp_raw))

        self.data = {
            "compensated_temp": round(compensated_temp, 1),
            "wind_adjustment": round(wind_adjustment, 1),
            "solar_adjustment": round(-solar_adjustment, 1),  # Negative since it reduces temp
            "heat_demand_adjustment": round(heat_demand_adjustment, 1),
            "flow_temp": round(flow_temp, 1),
        }

        _LOGGER.debug("CompCurve data: %s", self.data)

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

        entities_to_track = [self.outdoor_sensor]
        if self.wind_sensor:
            entities_to_track.append(self.wind_sensor)
        if self.sunlight_sensor:
            entities_to_track.append(self.sunlight_sensor)
        if self.heat_demand_sensor:
            entities_to_track.append(self.heat_demand_sensor)

        self._unsub_tracker = async_track_state_change_event(
            self.hass,
            entities_to_track,
            self._async_source_changed,
        )

    async def async_stop_tracking(self) -> None:
        """Stop tracking source entities."""
        if self._unsub_tracker:
            self._unsub_tracker()
            self._unsub_tracker = None


class CompCurveMainSensor(SensorEntity):
    """Main sensor that shows the calculated flow temperature."""

    _attr_has_entity_name = True
    _attr_name = "Target Flow Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:thermometer-water"

    def __init__(self, coordinator: CompCurveCoordinator) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_flow_temp"
        self._remove_listener: Callable[[], None] | None = None

    @property
    def device_info(self):
        """Return device info."""
        return self._coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the flow temperature."""
        return self._coordinator.data.get("flow_temp")

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        c = self._coordinator
        return {
            "heat_curve": c.heat_curve,
            "base_temp": c.base_temp,
            "min_flow_temp": c.min_flow,
            "max_flow_temp": c.max_flow,
            "scale_factor": c.scale_factor,
            "exponent": c.exponent,
            "wind_coefficient": c.wind_coefficient,
            "wind_exponent": c.wind_exponent,
            "solar_coefficient": c.solar_coefficient,
            "heat_demand_coefficient": c.heat_demand_coefficient,
            "formula": f"{c.scale_factor} × (HC × ΔT)^{c.exponent} + Tbase + {c.wind_coefficient} × wind^{c.wind_exponent} - {c.solar_coefficient} × sun + {c.heat_demand_coefficient} × demand",
        }

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


class CompCurveComponentSensor(SensorEntity):
    """Diagnostic sensor showing individual components."""

    _attr_has_entity_name = True
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: CompCurveCoordinator,
        description: CompCurveSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._remove_listener: Callable[[], None] | None = None
        # Explicitly set entity_category from description
        if description.entity_category:
            self._attr_entity_category = description.entity_category

    @property
    def device_info(self):
        """Return device info."""
        return self._coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self._coordinator.data)

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        self._remove_listener = self._coordinator.add_listener(
            self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is removed from hass."""
        if self._remove_listener:
            self._remove_listener()
