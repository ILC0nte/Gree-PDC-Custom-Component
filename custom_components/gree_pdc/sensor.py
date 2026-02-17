import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

@dataclass
class GreePDCSensorEntityDescription(SensorEntityDescription):
    """Custom description for Gree PDC sensors."""
    transform: Callable[[dict], Any] | None = None

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
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: GreePDCSensorEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
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
        
        if self.entity_description.transform:
            return self.entity_description.transform(data)
        
        return data.get(self.entity_description.key)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    from .select import MODE_ID_TO_KEY
    
    descriptions = [
        # Main Temperatures
        GreePDCSensorEntityDescription(
            key="in_water_temp",
            translation_key="in_water_temp",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            transform=lambda d: parse_temp(d.get("AllInWatTemHi"), d.get("AllInWatTemLo")),
        ),
        GreePDCSensorEntityDescription(
            key="out_water_temp",
            translation_key="out_water_temp",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            transform=lambda d: parse_temp(d.get("AllOutWatTemHi"), d.get("AllOutWatTemLo")),
        ),
        GreePDCSensorEntityDescription(
            key="temp_dhw",
            translation_key="temp_dhw",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            transform=lambda d: parse_temp(d.get("WatBoxTemHi"), d.get("WatBoxTemLo")),
        ),
        GreePDCSensorEntityDescription(
            key="room_temp",
            translation_key="room_temp",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            transform=lambda d: parse_temp(d.get("RmoHomTemHi"), d.get("RmoHomTemLo")),
        ),
        GreePDCSensorEntityDescription(
            key="mode",
            translation_key="operation_mode",
            transform=lambda d: MODE_ID_TO_KEY.get(d.get("Mod")),
        ),
    ]
    
    async_add_entities([GreePDCSensor(coordinator, entry, desc) for desc in descriptions])

