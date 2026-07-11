"""HomeKit TV proxy media player for Apple TV HomeKit Enhanced."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, override

from homeassistant.components.homekit.const import (
    ATTR_KEY_NAME,
    EVENT_HOMEKIT_TV_REMOTE_KEY_PRESSED,
    KEY_ARROW_DOWN,
    KEY_ARROW_LEFT,
    KEY_ARROW_RIGHT,
    KEY_ARROW_UP,
    KEY_BACK,
    KEY_EXIT,
    KEY_FAST_FORWARD,
    KEY_NEXT_TRACK,
    KEY_PLAY_PAUSE,
    KEY_PREVIOUS_TRACK,
    KEY_REWIND,
    KEY_SELECT,
)
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_INPUT_SOURCE_LIST,
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_VOLUME_MUTED,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_SELECT_SOURCE,
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_SUPPORTED_FEATURES,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_PLAY,
    SERVICE_MEDIA_PLAY_PAUSE,
    SERVICE_MEDIA_PREVIOUS_TRACK,
    SERVICE_MEDIA_STOP,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_SET,
    SERVICE_VOLUME_UP,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import AppleTVEnhancedEntity
from .helpers import (
    SOURCE_CLOSE_APPS,
    SOURCE_HOME,
    build_close_apps_sequence,
    build_homekit_sources,
)
from .homekit import async_ensure_homekit_accessory
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData

_LOGGER = logging.getLogger(__name__)

REMOTE_KEY_COMMANDS = {
    KEY_ARROW_DOWN: "down",
    KEY_ARROW_LEFT: "left",
    KEY_ARROW_RIGHT: "right",
    KEY_ARROW_UP: "up",
    KEY_BACK: "menu",
    KEY_EXIT: "home",
    KEY_FAST_FORWARD: "skip_forward",
    KEY_NEXT_TRACK: "next",
    KEY_PREVIOUS_TRACK: "previous",
    KEY_REWIND: "skip_backward",
    KEY_SELECT: "select",
}

REMOTE_KEY_MEDIA_SERVICES = {
    KEY_PLAY_PAUSE: SERVICE_MEDIA_PLAY_PAUSE,
}

# Only advertise services implemented by this proxy. Mirroring every source
# feature would expose controls such as browse, seek, repeat, and shuffle even
# though this integration does not delegate those methods.
FORWARDED_MEDIA_PLAYER_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_STEP
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleTVEnhancedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the HomeKit TV proxy media player."""
    async_add_entities([AppleTVHomeKitMediaPlayer(entry, entry.runtime_data)])


class AppleTVHomeKitMediaPlayer(AppleTVEnhancedEntity, MediaPlayerEntity):
    """Media player that exposes Apple TV as a HomeKit Television accessory."""

    _attr_device_class = MediaPlayerDeviceClass.TV

    def __init__(
        self,
        entry: AppleTVEnhancedConfigEntry,
        runtime_data: AppleTVEnhancedRuntimeData,
    ) -> None:
        """Initialize the HomeKit TV proxy."""
        super().__init__(entry, runtime_data, "homekit_media_player")
        self._entry = entry
        self._attr_name = "HomeKit TV"

    @override
    async def async_added_to_hass(self) -> None:
        """Subscribe to source and HomeKit remote-key events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_HOMEKIT_TV_REMOTE_KEY_PRESSED,
                self._async_homekit_remote_key_pressed,
            )
        )

        if self.runtime_data.enable_homekit_qr:
            self._entry.async_create_background_task(
                self.hass,
                self._async_ensure_homekit_accessory_when_ready(),
                f"{self._entry.domain} ensure HomeKit accessory",
            )

    @property
    def state(self) -> str | None:
        """Mirror the official media player state."""
        source_state = self.source_state
        return source_state.state if source_state else None

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Expose only source capabilities implemented by this proxy."""
        features = MediaPlayerEntityFeature(
            self._source_attr(ATTR_SUPPORTED_FEATURES, 0)
        )
        return (
            features & FORWARDED_MEDIA_PLAYER_FEATURES
        ) | MediaPlayerEntityFeature.SELECT_SOURCE

    @property
    def source(self) -> str | None:
        """Return current app/source."""
        return self._source_attr(ATTR_INPUT_SOURCE) or self.app_name

    @property
    def source_list(self) -> list[str]:
        """Expose launcher actions and Apple TV app list as HomeKit inputs."""
        return list(build_homekit_sources(self._source_attr(ATTR_INPUT_SOURCE_LIST, [])))

    @property
    def volume_level(self) -> float | None:
        """Mirror volume level."""
        return self._source_attr(ATTR_MEDIA_VOLUME_LEVEL)

    @property
    def is_volume_muted(self) -> bool | None:
        """Mirror mute state."""
        return self._source_attr(ATTR_MEDIA_VOLUME_MUTED)

    @property
    def app_id(self) -> str | None:
        """Mirror current app id."""
        return self._source_attr("app_id")

    @property
    def app_name(self) -> str | None:
        """Mirror current app name."""
        return self._source_attr("app_name")

    @property
    def media_content_id(self) -> str | None:
        """Mirror media content id."""
        return self._source_attr("media_content_id")

    @property
    def media_content_type(self) -> str | None:
        """Mirror media content type."""
        return self._source_attr("media_content_type")

    @property
    def media_title(self) -> str | None:
        """Mirror media title."""
        return self._source_attr("media_title")

    @property
    def media_artist(self) -> str | None:
        """Mirror media artist."""
        return self._source_attr("media_artist")

    @property
    def media_album_name(self) -> str | None:
        """Mirror media album."""
        return self._source_attr("media_album_name")

    @property
    def media_series_title(self) -> str | None:
        """Mirror media series title."""
        return self._source_attr("media_series_title")

    @property
    def media_season(self) -> str | None:
        """Mirror media season."""
        return self._source_attr("media_season")

    @property
    def media_episode(self) -> str | None:
        """Mirror media episode."""
        return self._source_attr("media_episode")

    @property
    def media_duration(self) -> int | None:
        """Mirror media duration."""
        return self._source_attr("media_duration")

    @property
    def media_position(self) -> int | None:
        """Mirror media position."""
        return self._source_attr("media_position")

    @property
    def media_position_updated_at(self) -> Any:
        """Mirror media position timestamp."""
        return self._source_attr("media_position_updated_at")

    @property
    def media_image_url(self) -> str | None:
        """Mirror media image URL."""
        return self._source_attr("media_image_url")

    @override
    async def async_select_source(self, source: str) -> None:
        """Route HomeKit input selection to launcher actions or app launch."""
        if source == SOURCE_HOME:
            await self._async_send_remote_command("home")
            return

        if source == SOURCE_CLOSE_APPS:
            self._entry.async_create_background_task(
                self.hass,
                self._async_close_apps(),
                f"{self._entry.domain} close apps",
            )
            return

        await self._async_call_media_service(
            SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: source}
        )

    @override
    async def async_turn_on(self) -> None:
        """Turn on the source Apple TV."""
        await self._async_call_media_service(SERVICE_TURN_ON)

    @override
    async def async_turn_off(self) -> None:
        """Turn off the source Apple TV."""
        await self._async_call_media_service(SERVICE_TURN_OFF)

    @override
    async def async_media_play(self) -> None:
        """Play media."""
        await self._async_call_media_service(SERVICE_MEDIA_PLAY)

    @override
    async def async_media_pause(self) -> None:
        """Pause media."""
        await self._async_call_media_service(SERVICE_MEDIA_PAUSE)

    @override
    async def async_media_play_pause(self) -> None:
        """Toggle play/pause."""
        await self._async_call_media_service(SERVICE_MEDIA_PLAY_PAUSE)

    @override
    async def async_media_stop(self) -> None:
        """Stop media."""
        await self._async_call_media_service(SERVICE_MEDIA_STOP)

    @override
    async def async_media_next_track(self) -> None:
        """Skip to next track."""
        await self._async_call_media_service(SERVICE_MEDIA_NEXT_TRACK)

    @override
    async def async_media_previous_track(self) -> None:
        """Skip to previous track."""
        await self._async_call_media_service(SERVICE_MEDIA_PREVIOUS_TRACK)

    @override
    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level."""
        await self._async_call_media_service(
            SERVICE_VOLUME_SET, {ATTR_MEDIA_VOLUME_LEVEL: volume}
        )

    @override
    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute volume."""
        await self._async_call_media_service(
            SERVICE_VOLUME_MUTE, {ATTR_MEDIA_VOLUME_MUTED: mute}
        )

    @override
    async def async_volume_up(self) -> None:
        """Raise volume."""
        await self._async_call_media_service(SERVICE_VOLUME_UP)

    @override
    async def async_volume_down(self) -> None:
        """Lower volume."""
        await self._async_call_media_service(SERVICE_VOLUME_DOWN)

    def _source_attr(self, key: str, default: Any = None) -> Any:
        """Return an attribute from the official media player state."""
        source_state = self.source_state
        if source_state is None:
            return default
        return source_state.attributes.get(key, default)

    async def _async_ensure_homekit_accessory_when_ready(self) -> None:
        """Wait until the proxy has state before starting the HomeKit flow."""
        for _ in range(5):
            if self.hass.states.get(self.entity_id) is not None:
                await async_ensure_homekit_accessory(
                    self.hass, self._entry, self.entity_id
                )
                return
            await asyncio.sleep(1)

        _LOGGER.warning(
            "Could not create HomeKit accessory because %s has no state",
            self.entity_id,
        )

    async def _async_call_media_service(
        self, service: str, data: dict[str, Any] | None = None
    ) -> None:
        """Delegate a media_player service to the official Apple TV entity."""
        await self.hass.services.async_call(
            MEDIA_PLAYER_DOMAIN,
            service,
            {ATTR_ENTITY_ID: self.runtime_data.media_player_entity_id, **(data or {})},
            blocking=True,
        )

    async def _async_send_remote_command(self, command: str) -> None:
        """Send one remote command to the official Apple TV remote entity."""
        remote_entity_id = self.runtime_data.remote_entity_id
        if remote_entity_id is None:
            _LOGGER.debug("No Apple TV remote entity found for command %s", command)
            return

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {ATTR_ENTITY_ID: remote_entity_id, "command": command},
            blocking=True,
        )

    async def _async_close_apps(self) -> None:
        """Run the Homebridge-compatible close-apps sequence."""
        async with self.runtime_data.close_apps_lock:
            for command, delay in build_close_apps_sequence(
                self.runtime_data.close_apps_count
            ):
                await self._async_send_remote_command(command)
                if delay:
                    await asyncio.sleep(delay)

    @callback
    def _async_homekit_remote_key_pressed(self, event: Event) -> None:
        """Map HomeKit TV remote-key events to Apple TV remote commands."""
        if event.data.get(ATTR_ENTITY_ID) != self.entity_id:
            return

        key_name = event.data.get(ATTR_KEY_NAME)
        if not isinstance(key_name, str):
            return

        if service := REMOTE_KEY_MEDIA_SERVICES.get(key_name):
            self._entry.async_create_background_task(
                self.hass,
                self._async_call_media_service(service),
                f"{self._entry.domain} HomeKit media key",
            )
            return

        if command := REMOTE_KEY_COMMANDS.get(key_name):
            self._entry.async_create_background_task(
                self.hass,
                self._async_send_remote_command(command),
                f"{self._entry.domain} HomeKit remote key",
            )
