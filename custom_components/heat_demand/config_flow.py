"""Config flow for Heat Demand integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CLIMATE_ENTITIES,
    CONF_OVERSHOOT_THRESHOLD,
    DEFAULT_OVERSHOOT_THRESHOLD,
    DOMAIN,
)


class HeatDemandConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Heat Demand."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return HeatDemandOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - climate entity selection."""
        if user_input is not None:
            return self.async_create_entry(
                title="Heat Demand",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIMATE_ENTITIES): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="climate",
                            multiple=True,
                        ),
                    ),
                    vol.Optional(
                        CONF_OVERSHOOT_THRESHOLD,
                        default=DEFAULT_OVERSHOOT_THRESHOLD,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.0,
                            max=10.0,
                            step=0.1,
                            unit_of_measurement="°C",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
        )


class HeatDemandOptionsFlow(OptionsFlow):
    """Handle options flow for Heat Demand."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle climate entity selection in options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=user_input,
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CLIMATE_ENTITIES,
                        default=self._config_entry.data.get(CONF_CLIMATE_ENTITIES, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="climate",
                            multiple=True,
                        ),
                    ),
                    vol.Optional(
                        CONF_OVERSHOOT_THRESHOLD,
                        default=self._config_entry.data.get(
                            CONF_OVERSHOOT_THRESHOLD, DEFAULT_OVERSHOOT_THRESHOLD
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.0,
                            max=10.0,
                            step=0.1,
                            unit_of_measurement="°C",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
        )
