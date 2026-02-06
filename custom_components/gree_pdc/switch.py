import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class GreePDCGenericSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, client, entry, name, key, unique_id_suffix, icon):
        super().__init__(coordinator)
        self._client = client
        self._entry_id = entry.entry_id
        self._key = key
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )
        # Set the entity_id to match the requested schema
        self.entity_id = f"switch.{device_name.lower().replace(' ', '_')}_{unique_id_suffix}"

    @property
    def is_on(self):
        data = self.coordinator.data
        if data is None:
            return None
        return data.get(self._key) == 1

    async def async_turn_on(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self._key: 1}
        )
        if success:
            self.coordinator.data[self._key] = 1
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self._key: 0}
        )
        if success:
            self.coordinator.data[self._key] = 0
            self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = [
        GreePDCGenericSwitch(coordinator, client, entry, "Power Switch", "Pow", "power_switch", "mdi:power"),
        GreePDCGenericSwitch(coordinator, client, entry, "Quiet Mode Switch", "Quiet", "quiet_mode_switch", "mdi:volume-mute"),
    ]
    
    async_add_entities(entities)
