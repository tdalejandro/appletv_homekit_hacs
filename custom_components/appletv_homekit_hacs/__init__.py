"""Apple TV HomeKit Enhanced integration."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er

from .const import APPLE_TV_DOMAIN, CONF_MEDIA_PLAYER_ENTITY_ID, PLATFORMS
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData


async def async_setup_entry(
    hass: HomeAssistant, entry: AppleTVEnhancedConfigEntry
) -> bool:
    """Set up Apple TV HomeKit Enhanced from a config entry."""
    entity_registry = er.async_get(hass)
    media_player_entity_id = entry.data[CONF_MEDIA_PLAYER_ENTITY_ID]
    source_entity = entity_registry.async_get(media_player_entity_id)

    if source_entity is None:
        raise ConfigEntryNotReady(
            f"Source entity {media_player_entity_id} is not registered"
        )

    source_entry = _source_config_entry(hass, source_entity.config_entry_id)
    entry.runtime_data = AppleTVEnhancedRuntimeData(
        media_player_entity_id=media_player_entity_id,
        remote_entity_id=_find_remote_entity_id(entity_registry, source_entity),
        source_unique_id=source_entry.unique_id if source_entry else None,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AppleTVEnhancedConfigEntry
) -> bool:
    """Unload an Apple TV HomeKit Enhanced config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _source_config_entry(
    hass: HomeAssistant, config_entry_id: str | None
) -> ConfigEntry[Any] | None:
    """Resolve the source Apple TV config entry."""
    if config_entry_id is None:
        return None
    return hass.config_entries.async_get_entry(config_entry_id)


def _find_remote_entity_id(
    entity_registry: er.EntityRegistry, source_entity: er.RegistryEntry
) -> str | None:
    """Find the official Apple TV remote on the same device."""
    if source_entity.device_id is None:
        return None

    for candidate in entity_registry.entities.get_entries_for_device_id(
        source_entity.device_id
    ):
        if candidate.domain == "remote" and candidate.platform == APPLE_TV_DOMAIN:
            return candidate.entity_id

    return None
