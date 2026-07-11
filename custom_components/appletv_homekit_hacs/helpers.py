"""Pure state mapping helpers for Apple TV HomeKit Enhanced."""

from typing import Any

MEDIA_TYPE_ALIASES = {
    "audio": "music",
    "episode": "tv",
    "movie": "video",
    "music": "music",
    "song": "music",
    "tv": "tv",
    "tvshow": "tv",
    "tv_show": "tv",
    "video": "video",
}


def normalized_media_type(value: Any) -> str:
    """Normalize Home Assistant media types to stable automation values."""
    if not isinstance(value, str) or not value.strip():
        return "unknown"

    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return MEDIA_TYPE_ALIASES.get(normalized, "unknown")


def media_type_matches(value: Any, expected: str) -> bool:
    """Return whether a media type maps to the expected category."""
    return normalized_media_type(value) == expected


def playback_state_matches(value: Any, expected: str) -> bool:
    """Return whether a playback state matches the expected value."""
    return isinstance(value, str) and value.lower() == expected

