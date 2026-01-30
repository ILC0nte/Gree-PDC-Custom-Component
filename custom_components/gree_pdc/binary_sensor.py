import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)

class GreePDCBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, name, key, unique_id_suffix, device_class=None, transform=None):
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        device_name = entry.data.get(CONF_NAME, "Gree PDC")
        self._attr_name = f"{device_name} {name}"
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_class = device_class
        self._transform = transform
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=device_name,
            manufacturer="Gree",
            model="Versati",
        )
        # Set the entity_id to match the requested schema
        self.entity_id = f"binary_sensor.{device_name.lower().replace(' ', '_')}_{unique_id_suffix}"

    @property
    def is_on(self):
        data = self.coordinator.data
        if data is None:
            return None
        
        if self._transform:
            return self._transform(data)
            
        return data.get(self._key) == 1

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = [
        GreePDCBinarySensor(coordinator, entry, "Power", "Pow", "pdc_power", BinarySensorDeviceClass.POWER),
        GreePDCBinarySensor(coordinator, entry, "Quiet Mode", "Quiet", "pdc_quiet_mode"),
        GreePDCBinarySensor(coordinator, entry, "Boiler Heat Resistance", "WatBoxElcHeRunSta", "boiler_heat_resistance"),
        GreePDCBinarySensor(coordinator, entry, "Rapid DHW", "FastHtWter", "pdc_rapid_dhw"),
        
        # Function status based on Mod
        GreePDCBinarySensor(coordinator, entry, "Heating State", "Mod", "heating_state", 
                            transform=lambda d: d.get("Mod") in (1, 4)),
        GreePDCBinarySensor(coordinator, entry, "Cooling State", "Mod", "cooling_state", 
                            transform=lambda d: d.get("Mod") in (3, 5)),
        GreePDCBinarySensor(coordinator, entry, "DHW State", "Mod", "dhw_state", 
                            transform=lambda d: d.get("Mod") in (2, 3, 4)),
    ]
    
    async_add_entities(entities)
