import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .api import HarviaSaunaAPI
from .constants import DOMAIN  # Ensure constants.py defines your DOMAIN

class HarviaSaunaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for your_component."""

    VERSION = 1  # Config flow version
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        # Check if we already have a configuration
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Process submitted data
        if user_input is not None:
            # Validate credentials
            api =  HarviaSaunaAPI(user_input[CONF_USERNAME], user_input[CONF_PASSWORD],self.hass)
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
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return HarviaSaunaOptionsFlowHandler(config_entry)

class HarviaSaunaOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        errors = {}

        if user_input is not None:
            # Validate credentials
            api =  HarviaSaunaAPI(user_input[CONF_USERNAME], user_input[CONF_PASSWORD],self.hass)
            valid = await api.authenticate()
            if valid:
                return self.async_create_entry(title="Harvia Sauna", data=user_input)
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME, default=self._config_entry.data.get(CONF_USERNAME)): str,
                vol.Required(CONF_PASSWORD, default=self._config_entry.data.get(CONF_PASSWORD)): str,
            }),
            errors=errors
        )