"""Constants for Apple TV HomeKit Enhanced."""

from homeassistant.const import Platform

APPLE_TV_DOMAIN = "apple_tv"
CONF_MEDIA_PLAYER_ENTITY_ID = "media_player_entity_id"
DOMAIN = "appletv_homekit_hacs"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SENSOR]

