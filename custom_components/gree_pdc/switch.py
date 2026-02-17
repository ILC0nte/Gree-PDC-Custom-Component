import logging
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class GreePDCSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, client, entry, description: SwitchEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._client = client
        self._entry_id = entry.entry_id
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )

    @property
    def is_on(self):
        data = self.coordinator.data
        if data is None:
            return None
        return data.get(self.entity_description.key) == 1

    async def async_turn_on(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self.entity_description.key: 1}
        )
        if success:
            if self.coordinator.data is not None:
                self.coordinator.data[self.entity_description.key] = 1
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self.entity_description.key: 0}
        )
        if success:
            if self.coordinator.data is not None:
                self.coordinator.data[self.entity_description.key] = 0
            self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    descriptions = [
        SwitchEntityDescription(
            key="Pow",
            translation_key="power_switch",
            icon="mdi:power",
        ),
        SwitchEntityDescription(
            key="Quiet",
            translation_key="quiet_mode_switch",
            icon="mdi:volume-mute",
        ),
    ]
    
    async_add_entities([GreePDCSwitch(coordinator, client, entry, desc) for desc in descriptions])

