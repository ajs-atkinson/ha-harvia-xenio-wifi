import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.selector import (
    NumberSelector, NumberSelectorConfig, NumberSelectorMode,
)
from .api import HarviaSaunaAPI
from .constants import DOMAIN

CONF_STOVE_RATED_POWER = "stove_rated_power_kw"


class HarviaSaunaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Harvia Sauna."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            api = HarviaSaunaAPI(user_input[CONF_USERNAME], user_input[CONF_PASSWORD], self.hass)
            valid = await api.authenticate()
            if valid:
                return self.async_create_entry(title="Harvia Sauna", data=user_input)
            else:
                errors["base"] = "invalid_auth"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HarviaSaunaOptionsFlowHandler(config_entry)


class HarviaSaunaOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow: set the stove rated power so stove energy (kWh) can be derived."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current = self._config_entry.options.get(CONF_STOVE_RATED_POWER, 0)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_STOVE_RATED_POWER, default=current): NumberSelector(
                    NumberSelectorConfig(min=0, max=30, step=0.1, mode=NumberSelectorMode.BOX, unit_of_measurement="kW")
                ),
            }),
        )
