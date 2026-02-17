import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity, 
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

@dataclass
class GreePDCBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Custom description for Gree PDC binary sensors."""
    transform: Callable[[dict], Any] | None = None

class GreePDCBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: GreePDCBinarySensorEntityDescription):
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
    def is_on(self):
        data = self.coordinator.data
        if data is None:
            return None
        
        if self.entity_description.transform:
            return self.entity_description.transform(data)
            
        return data.get(self.entity_description.key) == 1

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    descriptions = [
        GreePDCBinarySensorEntityDescription(
            key="power",
            translation_key="power",
            device_class=BinarySensorDeviceClass.POWER,
        ),
        GreePDCBinarySensorEntityDescription(
            key="quiet_mode",
            translation_key="quiet_mode",
        ),
        GreePDCBinarySensorEntityDescription(
            key="boiler_heat_resistance",
            translation_key="boiler_heat_resistance",
        ),
        GreePDCBinarySensorEntityDescription(
            key="rapid_dhw",
            translation_key="rapid_dhw",
        ),
        GreePDCBinarySensorEntityDescription(
            key="dhw_boiler_equipped",
            translation_key="dhw_boiler_equipped",
        ),
        GreePDCBinarySensorEntityDescription(
            key="antifreeze_function",
            translation_key="antifreeze_function",
        ),
        GreePDCBinarySensorEntityDescription(
            key="defrost_cycle",
            translation_key="defrost_cycle",
        ),
        GreePDCBinarySensorEntityDescription(
            key="heating_state",
            translation_key="heating_state",
            transform=lambda d: d.get("Mod") in (1, 4),
        ),
        GreePDCBinarySensorEntityDescription(
            key="cooling_state",
            translation_key="cooling_state",
            transform=lambda d: d.get("Mod") in (3, 5),
        ),
        GreePDCBinarySensorEntityDescription(
            key="dhw_state",
            translation_key="dhw_state",
            transform=lambda d: d.get("Mod") in (2, 3, 4),
        ),
    ]
    
    async_add_entities([GreePDCBinarySensor(coordinator, entry, desc) for desc in descriptions])

