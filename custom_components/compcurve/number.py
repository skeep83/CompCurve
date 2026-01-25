"""Number platform for Compensation Curve integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_EXPONENT,
    CONF_HEAT_CURVE,
    CONF_MAX_FLOW_TEMP,
    CONF_MIN_FLOW_TEMP,
    CONF_SCALE_FACTOR,
    CONF_BASE_TEMP,
    CONF_SOLAR_COEFFICIENT,
    CONF_WIND_COEFFICIENT,
    CONF_WIND_EXPONENT,
    CONF_WIND_SPEED_SENSOR,
    CONF_SUNLIGHT_SENSOR,
    DEFAULT_EXPONENT,
    DEFAULT_HEAT_CURVE,
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
class CompCurveNumberEntityDescription(NumberEntityDescription):
    """Describes a CompCurve number entity."""

    conf_key: str = ""
    default_value: float = 0.0


BASIC_NUMBER_DESCRIPTIONS: tuple[CompCurveNumberEntityDescription, ...] = (
    CompCurveNumberEntityDescription(
        key="base_temp",
        name="Base Temperature",
        icon="mdi:home-thermometer",
        native_min_value=15,
        native_max_value=25,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_BASE_TEMP,
        default_value=DEFAULT_BASE_TEMP,
    ),
    CompCurveNumberEntityDescription(
        key="min_flow_temp",
        name="Min Flow Temperature",
        icon="mdi:thermometer-low",
        native_min_value=15,
        native_max_value=40,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_MIN_FLOW_TEMP,
        default_value=DEFAULT_MIN_FLOW_TEMP,
    ),
    CompCurveNumberEntityDescription(
        key="max_flow_temp",
        name="Max Flow Temperature",
        icon="mdi:thermometer-high",
        native_min_value=40,
        native_max_value=80,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_MAX_FLOW_TEMP,
        default_value=DEFAULT_MAX_FLOW_TEMP,
    ),
    CompCurveNumberEntityDescription(
        key="heat_curve",
        name="Heat Curve",
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0.3,
        native_max_value=2.0,
        native_step=0.05,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_HEAT_CURVE,
        default_value=DEFAULT_HEAT_CURVE,
    ),
)

ADVANCED_NUMBER_DESCRIPTIONS: tuple[CompCurveNumberEntityDescription, ...] = (
    CompCurveNumberEntityDescription(
        key="scale_factor",
        name="Scale Factor",
        icon="mdi:arrow-expand-vertical",
        native_min_value=1.0,
        native_max_value=5.0,
        native_step=0.1,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_SCALE_FACTOR,
        default_value=DEFAULT_SCALE_FACTOR,
    ),
    CompCurveNumberEntityDescription(
        key="exponent",
        name="Exponent",
        icon="mdi:exponent",
        native_min_value=0.5,
        native_max_value=1.2,
        native_step=0.05,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_EXPONENT,
        default_value=DEFAULT_EXPONENT,
    ),
)

WIND_NUMBER_DESCRIPTIONS: tuple[CompCurveNumberEntityDescription, ...] = (
    CompCurveNumberEntityDescription(
        key="wind_coefficient",
        name="Wind Coefficient",
        icon="mdi:weather-windy",
        native_min_value=0.0,
        native_max_value=1.0,
        native_step=0.05,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_WIND_COEFFICIENT,
        default_value=DEFAULT_WIND_COEFFICIENT,
    ),
    CompCurveNumberEntityDescription(
        key="wind_exponent",
        name="Wind Exponent",
        icon="mdi:exponent",
        native_min_value=0.5,
        native_max_value=1.2,
        native_step=0.05,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_WIND_EXPONENT,
        default_value=DEFAULT_WIND_EXPONENT,
    ),
)

SOLAR_NUMBER_DESCRIPTIONS: tuple[CompCurveNumberEntityDescription, ...] = (
    CompCurveNumberEntityDescription(
        key="solar_coefficient",
        name="Solar Coefficient",
        icon="mdi:white-balance-sunny",
        native_min_value=0.0,
        native_max_value=0.5,
        native_step=0.01,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        conf_key=CONF_SOLAR_COEFFICIENT,
        default_value=DEFAULT_SOLAR_COEFFICIENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Compensation Curve number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[NumberEntity] = []

    # Add basic parameters
    for description in BASIC_NUMBER_DESCRIPTIONS:
        entities.append(CompCurveNumber(coordinator, config_entry, description))

    # Add advanced parameters
    for description in ADVANCED_NUMBER_DESCRIPTIONS:
        entities.append(CompCurveNumber(coordinator, config_entry, description))

    # Add wind parameters only if wind sensor is configured
    if config_entry.data.get(CONF_WIND_SPEED_SENSOR):
        for description in WIND_NUMBER_DESCRIPTIONS:
            entities.append(CompCurveNumber(coordinator, config_entry, description))

    # Add solar parameters only if sunlight sensor is configured
    if config_entry.data.get(CONF_SUNLIGHT_SENSOR):
        for description in SOLAR_NUMBER_DESCRIPTIONS:
            entities.append(CompCurveNumber(coordinator, config_entry, description))

    async_add_entities(entities)


class CompCurveNumber(NumberEntity):
    """Number entity for CompCurve configuration parameters."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        description: CompCurveNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._config_entry = config_entry
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_entity_category = description.entity_category

    @property
    def device_info(self):
        """Return device info."""
        return self._coordinator.device_info

    @property
    def native_value(self) -> float:
        """Return the current value."""
        description = self.entity_description
        return self._config_entry.data.get(
            description.conf_key, description.default_value
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the configuration value."""
        description = self.entity_description
        new_data = dict(self._config_entry.data)
        new_data[description.conf_key] = value

        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data=new_data,
        )

        # Update coordinator parameters and recalculate
        setattr(self._coordinator, self._get_coordinator_attr(), value)
        self._coordinator._update_data()

        # Notify all listeners (sensors) to update
        for listener in self._coordinator._listeners:
            listener()

    def _get_coordinator_attr(self) -> str:
        """Get the coordinator attribute name for this parameter."""
        mapping = {
            CONF_HEAT_CURVE: "heat_curve",
            CONF_BASE_TEMP: "base_temp",
            CONF_MIN_FLOW_TEMP: "min_flow",
            CONF_MAX_FLOW_TEMP: "max_flow",
            CONF_SCALE_FACTOR: "scale_factor",
            CONF_EXPONENT: "exponent",
            CONF_WIND_COEFFICIENT: "wind_coefficient",
            CONF_WIND_EXPONENT: "wind_exponent",
            CONF_SOLAR_COEFFICIENT: "solar_coefficient",
        }
        return mapping.get(self.entity_description.conf_key, "")
