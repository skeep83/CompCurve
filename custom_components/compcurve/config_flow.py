"""Config flow for Compensation Curve integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_SUNLIGHT_SENSOR,
    CONF_WIND_SPEED_SENSOR,
    DOMAIN,
)


def get_sensor_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Get schema for sensor selection step."""
    defaults = defaults or {}
    schema = {
        vol.Required(
            CONF_OUTDOOR_TEMP_SENSOR,
            default=defaults.get(CONF_OUTDOOR_TEMP_SENSOR, ""),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        ),
    }

    # Optional sensors - only include default if one exists
    if defaults.get(CONF_WIND_SPEED_SENSOR):
        schema[vol.Optional(
            CONF_WIND_SPEED_SENSOR,
            default=defaults[CONF_WIND_SPEED_SENSOR],
        )] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        )
    else:
        schema[vol.Optional(CONF_WIND_SPEED_SENSOR)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        )

    if defaults.get(CONF_SUNLIGHT_SENSOR):
        schema[vol.Optional(
            CONF_SUNLIGHT_SENSOR,
            default=defaults[CONF_SUNLIGHT_SENSOR],
        )] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        )
    else:
        schema[vol.Optional(CONF_SUNLIGHT_SENSOR)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        )

    return vol.Schema(schema)


class CompCurveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Compensation Curve."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return CompCurveOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - sensor selection."""
        if user_input is not None:
            return self.async_create_entry(
                title="Compensation Curve",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=get_sensor_schema(),
        )


class CompCurveOptionsFlow(OptionsFlow):
    """Handle options flow for Compensation Curve."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle sensor selection in options."""
        if user_input is not None:
            # Preserve existing parameter values, only update sensors
            new_data = dict(self._config_entry.data)
            new_data.update(user_input)
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=new_data,
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=get_sensor_schema(dict(self._config_entry.data)),
        )
