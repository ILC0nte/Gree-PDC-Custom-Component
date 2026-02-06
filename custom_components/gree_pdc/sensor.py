import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

def parse_temp(hi, lo):
    try:
        hi_str = str(hi)
        if len(hi_str) > 1:
            val = hi_str[1:]
        else:
            val = hi_str
        return float(f"{val}.{lo}")
    except (ValueError, TypeError, IndexError):
        return None

class GreePDCSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, key, unique_id_suffix, device_class=None, unit=None, state_class=None, transform=None, translation_key=None):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_name = f"{device_name} {name}"
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._transform = transform
        self._attr_translation_key = translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )
        # Set the entity_id to match the requested schema
        self.entity_id = f"sensor.{device_name.lower().replace(' ', '_')}_{unique_id_suffix}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        
        if self._transform:
            return self._transform(data)
        
        return data.get(self._key)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    from .select import MODE_ID_TO_KEY
    
    entities = [
        # Main Temperatures
        GreePDCSensor(coordinator, entry, "In Water Temp", "temp_ritorno", "in_water_temp",
                      SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT,
                      lambda d: parse_temp(d.get("AllInWatTemHi"), d.get("AllInWatTemLo"))),
        GreePDCSensor(coordinator, entry, "Out Water Temp", "temp_mandata", "out_water_temp",
                      SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT,
                      lambda d: parse_temp(d.get("AllOutWatTemHi"), d.get("AllOutWatTemLo"))),
        GreePDCSensor(coordinator, entry, "Temp DHW", "temp_acs", "temp_dhw",
                      SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT,
                      lambda d: parse_temp(d.get("WatBoxTemHi"), d.get("WatBoxTemLo"))),
        GreePDCSensor(coordinator, entry, "Room Temp", "temp_ambiente", "room_temp",
                      SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT,
                      lambda d: parse_temp(d.get("RmoHomTemHi"), d.get("RmoHomTemLo"))),
        
        # Mode
        GreePDCSensor(coordinator, entry, "Mode", "Mod", "mode",
                      transform=lambda d: MODE_ID_TO_KEY.get(d.get("Mod")),
                      translation_key="operation_mode"),
    ]
    
    async_add_entities(entities)
