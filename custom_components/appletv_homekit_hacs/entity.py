"""Base entity for Apple TV HomeKit Enhanced."""

from typing import override

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, State, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import APPLE_TV_DOMAIN, DOMAIN
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData


class AppleTVEnhancedEntity(Entity):
    """Base entity driven by official Apple TV entity state changes."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        entry: AppleTVEnhancedConfigEntry,
        runtime_data: AppleTVEnhancedRuntimeData,
        key: str,
    ) -> None:
        """Initialize a derived entity."""
        self.runtime_data = runtime_data
        source_id = runtime_data.source_unique_id or runtime_data.media_player_entity_id
        self._attr_unique_id = f"{source_id}_{key}"
        via_device = (
            (APPLE_TV_DOMAIN, runtime_data.source_unique_id)
            if runtime_data.source_unique_id
            else None
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Open Home Community",
            model="Apple TV Enhanced helper",
            name=f"{entry.title} Enhanced",
            via_device=via_device,
        )

    @override
    async def async_added_to_hass(self) -> None:
        """Subscribe to state changes from source entities."""
        entity_ids = [self.runtime_data.media_player_entity_id]
        if self.runtime_data.remote_entity_id:
            entity_ids.append(self.runtime_data.remote_entity_id)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, entity_ids, self._async_source_state_changed
            )
        )

    @callback
    def _async_source_state_changed(self, event: Event) -> None:
        """Refresh this entity after a source entity changes."""
        self.async_write_ha_state()

    @property
    def source_state(self) -> State | None:
        """Return the current official media player state."""
        return self.hass.states.get(self.runtime_data.media_player_entity_id)

    @property
    def available(self) -> bool:
        """Return whether the official Apple TV media player is available."""
        state = self.source_state
        return state is not None and state.state not in {
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        }

