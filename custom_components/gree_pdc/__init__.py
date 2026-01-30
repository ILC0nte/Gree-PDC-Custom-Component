import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, Platform

from .const import DOMAIN, CONF_ID, CONF_KEY, STATUS_COLS, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .gree_api import GreePDCClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gree PDC from a config entry."""
    client = GreePDCClient(
        entry.data[CONF_HOST],
        entry.data[CONF_ID],
        entry.data[CONF_KEY]
    )

    # Use the scan interval from options, fallback to data, then to default
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, 
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    async def async_update_data():
        """Fetch data from Gree PDC."""
        try:
            # Get main status
            main_status = await hass.async_add_executor_job(client.get_values, STATUS_COLS)
            
            data = {}
            if main_status:
                data.update(dict(zip(main_status['cols'], main_status['dat'])))
            
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="gree_pdc",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    # Add options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
