"""Pure state mapping helpers for Apple TV HomeKit Enhanced."""

from typing import Any

DEFAULT_CLOSE_APPS_COUNT = 15
MAX_CLOSE_APPS_COUNT = 35
MAX_HOMEKIT_SOURCES = 90
MIN_CLOSE_APPS_COUNT = 5
SOURCE_CLOSE_APPS = "Cerrar Apps"
SOURCE_HOME = "Inicio"

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


def clamp_close_apps_count(value: Any) -> int:
    """Clamp the close-apps sweep count to the supported tvOS launcher range."""
    try:
        count = int(value)
    except (TypeError, ValueError):
        return DEFAULT_CLOSE_APPS_COUNT

    return max(MIN_CLOSE_APPS_COUNT, min(MAX_CLOSE_APPS_COUNT, count))


def build_close_apps_sequence(app_count: Any) -> tuple[tuple[str, float], ...]:
    """Build the Homebridge-compatible command sequence for closing apps."""
    count = clamp_close_apps_count(app_count)
    sequence: list[tuple[str, float]] = [
        ("home", 0.1),
        ("home", 0.8),
        ("left", 0.3),
    ]

    for _ in range(count):
        sequence.extend((("up", 0.05), ("up", 0.6)))

    sequence.append(("home", 0.0))
    return tuple(sequence)


def build_homekit_sources(
    apps: Any, max_sources: int = MAX_HOMEKIT_SOURCES
) -> tuple[str, ...]:
    """Return HomeKit TV inputs with launcher actions before app sources."""
    candidates = [SOURCE_HOME, SOURCE_CLOSE_APPS]
    if isinstance(apps, (list, tuple, set)):
        candidates.extend(apps)

    sources: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        source = candidate.strip()
        if not source or source in seen:
            continue
        sources.append(source)
        seen.add(source)
        if len(sources) >= max_sources:
            break

    return tuple(sources)
