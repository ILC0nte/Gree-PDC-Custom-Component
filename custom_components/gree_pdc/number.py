import logging
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class GreePDCNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, client, entry, name, key, unique_id_suffix, min_val, max_val, step=1):
        super().__init__(coordinator)
        self._client = client
        self._entry_id = entry.entry_id
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_name = f"{device_name} {name}"
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )
        # Set the entity_id to match the requested schema
        self.entity_id = f"number.{device_name.lower().replace(' ', '_')}_{unique_id_suffix}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        return data.get(self._key)

    async def async_set_native_value(self, value):
        success = await self.hass.async_add_executor_job(
            self._client.set_values, {self._key: int(value)}
        )
        if success:
            self.coordinator.data[self._key] = int(value)
            self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = [
        GreePDCNumber(coordinator, client, entry, "Setpoint DHW", "WatBoxTemSet", "pdc_setpoint_dhw", 30, 60),
        GreePDCNumber(coordinator, client, entry, "Setpoint Heating Out Temp", "HeWatOutTemSet", "pdc_setpoint_heating_out_temp", 20, 50),
        GreePDCNumber(coordinator, client, entry, "Setpoint Cooling Out Temp", "CoWatOutTemSet", "pdc_setpoint_cooling_out_temp", 7, 25),
        GreePDCNumber(coordinator, client, entry, "Setpoint Heating Room Temp", "HeHomTemSet", "pdc_setpoint_heating_room_temp", 16, 30),
        GreePDCNumber(coordinator, client, entry, "Setpoint Cooling Room Temp", "CoHomTemSet", "pdc_setpoint_cooling_room_temp", 16, 30),
    ]
    
    async_add_entities(entities)
