import logging
import asyncio
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, Platform

from .const import DOMAIN, CONF_ID, CONF_KEY, STATUS_COLS, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, CONF_NAME
from .gree_api import GreePDCClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gree PDC from a config entry."""
    _LOGGER.debug("Setting up Gree PDC entry for host %s", entry.data[CONF_HOST])
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
            _LOGGER.debug("Fetching status from %s with columns %s", client.host, STATUS_COLS)
            try:
                main_status = await asyncio.wait_for(
                    hass.async_add_executor_job(client.get_values, STATUS_COLS),
                    timeout=3.0
                )
            except asyncio.TimeoutError:
                _LOGGER.error("Polling cycle timed out (3s) for %s", client.host)
                raise UpdateFailed("Polling cycle timed out")
            
            data = {}
            if main_status:
                data.update(dict(zip(main_status['cols'], main_status['dat'])))
            
            _LOGGER.debug("Data updated: %s", data if data else "no data")
            return data
        except UpdateFailed:
            raise
        except Exception as err:
            _LOGGER.error("Error communicating with API at %s: %s", client.host, err)
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

    _LOGGER.info("Gree PDC setup completed successfully for %s", entry.title)
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Gree PDC entry %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Gree PDC unloaded successfully")

    return unload_ok
