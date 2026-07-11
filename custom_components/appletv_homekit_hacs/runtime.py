"""Runtime models for Apple TV HomeKit Enhanced."""

import asyncio
from dataclasses import dataclass, field

from homeassistant.config_entries import ConfigEntry

from .helpers import DEFAULT_CLOSE_APPS_COUNT


@dataclass(slots=True)
class AppleTVEnhancedRuntimeData:
    """Resolved entities and device linkage for one config entry."""

    media_player_entity_id: str
    remote_entity_id: str | None
    source_unique_id: str | None
    enable_homekit_qr: bool = False
    close_apps_count: int = DEFAULT_CLOSE_APPS_COUNT
    homekit_entry_id: str | None = None
    close_apps_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    homekit_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


type AppleTVEnhancedConfigEntry = ConfigEntry[AppleTVEnhancedRuntimeData]
