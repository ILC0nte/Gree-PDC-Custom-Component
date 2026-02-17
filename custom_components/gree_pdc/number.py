import logging
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class GreePDCNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, client, entry, description: NumberEntityDescription):
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
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        return data.get(self.entity_description.key)

    async def async_set_native_value(self, value):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self.entity_description.key: int(value)}
        )
        if success:
            if self.coordinator.data is not None:
                self.coordinator.data[self.entity_description.key] = int(value)
            self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    descriptions = [
        NumberEntityDescription(
            key="WatBoxTemSet",
            translation_key="setpoint_dhw",
            native_min_value=30,
            native_max_value=60,
        ),
        NumberEntityDescription(
            key="HeWatOutTemSet",
            translation_key="setpoint_heating_out_temp",
            native_min_value=20,
            native_max_value=50,
        ),
        NumberEntityDescription(
            key="CoWatOutTemSet",
            translation_key="setpoint_cooling_out_temp",
            native_min_value=7,
            native_max_value=25,
        ),
        NumberEntityDescription(
            key="HeHomTemSet",
            translation_key="setpoint_heating_room_temp",
            native_min_value=16,
            native_max_value=30,
        ),
        NumberEntityDescription(
            key="CoHomTemSet",
            translation_key="setpoint_cooling_room_temp",
            native_min_value=16,
            native_max_value=30,
        ),
    ]
    
    async_add_entities([GreePDCNumber(coordinator, client, entry, desc) for desc in descriptions])

