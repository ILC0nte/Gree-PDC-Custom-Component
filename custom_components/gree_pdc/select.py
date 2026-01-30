import logging
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

MODE_ID_TO_KEY = {
    1: "heating",
    2: "acs",
    3: "cooling_acs",
    4: "heating_acs",
    5: "cooling"
}
MODE_KEY_TO_ID = {v: k for k, v in MODE_ID_TO_KEY.items()}

class GreePDCModeSelect(CoordinatorEntity, SelectEntity):
    _attr_translation_key = "pdc_operation_mode"

    def __init__(self, coordinator, client, entry):
        super().__init__(coordinator)
        self._client = client
        self._entry_id = entry.entry_id
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_name = f"{device_name} Operation Mode"
        self._attr_unique_id = f"{entry.entry_id}_pdc_operation_mode"
        self._attr_options = list(MODE_ID_TO_KEY.values())
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )
        # Set the entity_id to match the requested schema
        self.entity_id = f"select.{device_name.lower().replace(' ', '_')}_pdc_operation_mode"

    @property
    def current_option(self):
        data = self.coordinator.data
        if data is None:
            return None
        mod_val = data.get("Mod")
        return MODE_ID_TO_KEY.get(mod_val)

    async def async_select_option(self, option: str):
        mod_val = MODE_KEY_TO_ID.get(option)
        if mod_val is not None:
            success = await self.hass.async_add_executor_job(
                self._client.set_values, {"Mod": mod_val}
            )
            if success:
                if self.coordinator.data is not None:
                    self.coordinator.data["Mod"] = mod_val
                self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = [
        GreePDCModeSelect(coordinator, client, entry),
    ]
    
    async_add_entities(entities)
