"""Constants for Apple TV HomeKit Enhanced."""

from homeassistant.const import Platform

APPLE_TV_DOMAIN = "apple_tv"
CONF_CLOSE_APPS_COUNT = "close_apps_count"
CONF_ENABLE_HOMEKIT_QR = "enable_homekit_qr"
CONF_HOMEKIT_ENTRY_ID = "homekit_entry_id"
CONF_MEDIA_PLAYER_ENTITY_ID = "media_player_entity_id"
DOMAIN = "appletv_homekit_hacs"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
]
