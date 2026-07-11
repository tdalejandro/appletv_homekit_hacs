"""Runtime models for Apple TV HomeKit Enhanced."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry


@dataclass(slots=True)
class AppleTVEnhancedRuntimeData:
    """Resolved entities and device linkage for one config entry."""

    media_player_entity_id: str
    remote_entity_id: str | None
    source_unique_id: str | None


type AppleTVEnhancedConfigEntry = ConfigEntry[AppleTVEnhancedRuntimeData]

