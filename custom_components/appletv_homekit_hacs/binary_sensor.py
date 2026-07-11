"""Binary sensors for Apple TV HomeKit Enhanced."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import AppleTVEnhancedEntity
from .helpers import media_type_matches, playback_state_matches
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData


@dataclass(frozen=True, kw_only=True)
class AppleTVEnhancedBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a derived Apple TV binary sensor."""

    value_fn: Callable[[State], bool]


def _state_is(expected: str) -> Callable[[State], bool]:
    return lambda state: playback_state_matches(state.state, expected)


def _media_is(expected: str) -> Callable[[State], bool]:
    return lambda state: media_type_matches(
        state.attributes.get("media_content_type"), expected
    )


BINARY_SENSOR_DESCRIPTIONS = (
    AppleTVEnhancedBinarySensorDescription(
        key="playing", name="Playing", icon="mdi:play", value_fn=_state_is("playing")
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="paused", name="Paused", icon="mdi:pause", value_fn=_state_is("paused")
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="idle", name="Idle", icon="mdi:sleep", value_fn=_state_is("idle")
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="buffering",
        name="Buffering",
        icon="mdi:progress-clock",
        value_fn=_state_is("buffering"),
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="media_music",
        name="Music media",
        icon="mdi:music",
        value_fn=_media_is("music"),
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="media_video",
        name="Video media",
        icon="mdi:movie-open",
        value_fn=_media_is("video"),
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="media_tv",
        name="TV media",
        icon="mdi:television-classic",
        value_fn=_media_is("tv"),
    ),
    AppleTVEnhancedBinarySensorDescription(
        key="media_unknown",
        name="Unknown media",
        icon="mdi:help-circle-outline",
        value_fn=_media_is("unknown"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleTVEnhancedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Apple TV binary sensors."""
    async_add_entities(
        AppleTVEnhancedBinarySensor(entry, entry.runtime_data, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AppleTVEnhancedBinarySensor(AppleTVEnhancedEntity, BinarySensorEntity):
    """Binary sensor derived from an official Apple TV media player."""

    entity_description: AppleTVEnhancedBinarySensorDescription

    def __init__(
        self,
        entry: AppleTVEnhancedConfigEntry,
        runtime_data: AppleTVEnhancedRuntimeData,
        description: AppleTVEnhancedBinarySensorDescription,
    ) -> None:
        """Initialize a derived binary sensor."""
        super().__init__(entry, runtime_data, description.key)
        self.entity_description = description

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether the represented state is active."""
        state = self.source_state
        if state is None:
            return None
        return self.entity_description.value_fn(state)
