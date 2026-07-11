"""Sensors for Apple TV HomeKit Enhanced."""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import AppleTVEnhancedEntity
from .helpers import normalized_media_type
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData


@dataclass(frozen=True, kw_only=True)
class AppleTVEnhancedSensorDescription(SensorEntityDescription):
    """Describe a state or attribute sensor."""

    attribute: str | None = None


SENSOR_DESCRIPTIONS = (
    AppleTVEnhancedSensorDescription(
        key="playback_state", name="Playback state", icon="mdi:play-circle-outline"
    ),
    AppleTVEnhancedSensorDescription(
        key="active_app", name="Active app", icon="mdi:apps", attribute="source"
    ),
    AppleTVEnhancedSensorDescription(
        key="media_type",
        name="Media type",
        icon="mdi:multimedia",
        attribute="media_content_type",
    ),
    AppleTVEnhancedSensorDescription(
        key="title", name="Title", icon="mdi:format-title", attribute="media_title"
    ),
    AppleTVEnhancedSensorDescription(
        key="artist",
        name="Artist",
        icon="mdi:account-music",
        attribute="media_artist",
    ),
    AppleTVEnhancedSensorDescription(
        key="album", name="Album", icon="mdi:album", attribute="media_album_name"
    ),
    AppleTVEnhancedSensorDescription(
        key="series",
        name="Series",
        icon="mdi:television-classic",
        attribute="media_series_title",
    ),
    AppleTVEnhancedSensorDescription(
        key="position",
        name="Position",
        icon="mdi:progress-clock",
        attribute="media_position",
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    AppleTVEnhancedSensorDescription(
        key="duration",
        name="Duration",
        icon="mdi:timer-outline",
        attribute="media_duration",
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleTVEnhancedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up derived Apple TV sensors."""
    async_add_entities(
        AppleTVEnhancedSensor(entry, entry.runtime_data, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AppleTVEnhancedSensor(AppleTVEnhancedEntity, SensorEntity):
    """Sensor derived from an official Apple TV media player."""

    entity_description: AppleTVEnhancedSensorDescription

    def __init__(
        self,
        entry: AppleTVEnhancedConfigEntry,
        runtime_data: AppleTVEnhancedRuntimeData,
        description: AppleTVEnhancedSensorDescription,
    ) -> None:
        """Initialize a derived sensor."""
        super().__init__(entry, runtime_data, description.key)
        self.entity_description = description

    @property
    @override
    def native_value(self) -> Any:
        """Return the mirrored state or media attribute."""
        state: State | None = self.source_state
        if state is None:
            return None
        if self.entity_description.attribute is None:
            return state.state

        value = state.attributes.get(self.entity_description.attribute)
        if self.entity_description.key == "media_type":
            return normalized_media_type(value)
        return value

