"""Constants for the Gree PDC integration."""

DOMAIN = "gree_pdc"
CONF_ID = "id"
CONF_KEY = "key"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 7000
DEFAULT_SCAN_INTERVAL = 10
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 600

GENERIC_KEY = "a3K8Bx%2r8Y7#xDh"

# Status columns from gree_decode.py
STATUS_COLS = [
    "Pow", "Mod", "WatBoxTemSet", "HeWatOutTemSet", "CoWatOutTemSet",
    "HeHomTemSet", "CoHomTemSet", "Quiet", "AllInWatTemHi", "AllInWatTemLo",
    "AllOutWatTemHi", "AllOutWatTemLo", "WatBoxTemHi", "WatBoxTemLo",
    "WatBoxElcHeRunSta", "FastHtWter", "RmoHomTemHi", "RmoHomTemLo", "WatBoxExt",
    "SyAnFroRunSta", "AnFrzzRunSta"
]
