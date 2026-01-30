import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST
from .const import (
    DOMAIN, 
    CONF_ID, 
    CONF_KEY, 
    CONF_NAME,
    CONF_SCAN_INTERVAL, 
    DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL
)
from .gree_api import GreePDCClient

class GreePDCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._devices = []
        self._host = None
        self._selected_device = None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            try:
                self._devices = await self.hass.async_add_executor_job(
                    GreePDCClient.scan, self._host
                )
                if not self._devices:
                    errors["base"] = "cannot_connect"
                elif len(self._devices) == 1:
                    self._selected_device = self._devices[0]
                    return await self.async_step_name()
                else:
                    return await self.async_step_select()
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
            }),
            errors=errors,
        )

    async def async_step_select(self, user_input=None):
        if user_input is not None:
            device_id = user_input["device"]
            self._selected_device = next(d for d in self._devices if d["id"] == device_id)
            return await self.async_step_name()

        device_options = {d["id"]: f"{d['name']} ({d['host']})" for d in self._devices}
        return self.async_show_form(
            step_id="select",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_options),
            }),
        )

    async def async_step_name(self, user_input=None):
        errors = {}
        if user_input is not None:
            custom_name = user_input.get(CONF_NAME) or self._selected_device["name"]
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            
            # Perform binding
            client = GreePDCClient(self._selected_device["host"], self._selected_device["id"], "")
            success = await self.hass.async_add_executor_job(client.bind)
            
            if success:
                await self.async_set_unique_id(self._selected_device["id"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=custom_name,
                    data={
                        CONF_HOST: self._selected_device["host"],
                        CONF_ID: self._selected_device["id"],
                        CONF_KEY: client.device_key,
                        CONF_NAME: custom_name,
                        CONF_SCAN_INTERVAL: scan_interval,
                    }
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="name",
            data_schema=vol.Schema({
                vol.Optional(CONF_NAME, default=self._selected_device["name"]): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return GreePDCOptionsFlowHandler(config_entry)

class GreePDCOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Gree PDC options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Use the stored config entry
        current_interval = self._config_entry.options.get(CONF_SCAN_INTERVAL)
        if current_interval is None:
            current_interval = self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=int(current_interval),
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            }),
        )
