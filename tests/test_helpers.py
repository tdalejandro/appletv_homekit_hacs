"""Tests for pure Apple TV state mappings."""

import importlib.util
from pathlib import Path
import unittest

HELPERS_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "appletv_homekit_hacs"
    / "helpers.py"
)
SPEC = importlib.util.spec_from_file_location("appletv_helpers", HELPERS_PATH)
assert SPEC is not None and SPEC.loader is not None
HELPERS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPERS)


class MediaTypeTests(unittest.TestCase):
    """Verify media type normalization used by sensors."""

    def test_known_media_types(self) -> None:
        self.assertEqual(HELPERS.normalized_media_type("music"), "music")
        self.assertEqual(HELPERS.normalized_media_type("Movie"), "video")
        self.assertEqual(HELPERS.normalized_media_type("tv-show"), "tv")

    def test_unknown_media_types(self) -> None:
        self.assertEqual(HELPERS.normalized_media_type(None), "unknown")
        self.assertEqual(HELPERS.normalized_media_type("podcast"), "unknown")

    def test_media_type_match(self) -> None:
        self.assertTrue(HELPERS.media_type_matches("episode", "tv"))
        self.assertFalse(HELPERS.media_type_matches("song", "video"))


class PlaybackStateTests(unittest.TestCase):
    """Verify playback state comparisons."""

    def test_case_insensitive_match(self) -> None:
        self.assertTrue(HELPERS.playback_state_matches("PLAYING", "playing"))

    def test_non_string_does_not_match(self) -> None:
        self.assertFalse(HELPERS.playback_state_matches(None, "idle"))


class HomeKitSourceTests(unittest.TestCase):
    """Verify app source composition for the HomeKit TV accessory."""

    def test_launcher_actions_precede_apps(self) -> None:
        self.assertEqual(
            HELPERS.build_homekit_sources(["Netflix", "YouTube"]),
            ("Inicio", "Cerrar Apps", "Netflix", "YouTube"),
        )

    def test_duplicate_sources_are_removed(self) -> None:
        self.assertEqual(
            HELPERS.build_homekit_sources(["Netflix", "Cerrar Apps", "Netflix"]),
            ("Inicio", "Cerrar Apps", "Netflix"),
        )

    def test_maximum_sources_is_enforced(self) -> None:
        sources = HELPERS.build_homekit_sources(
            [f"App {index}" for index in range(100)], max_sources=5
        )
        self.assertEqual(len(sources), 5)


class CloseAppsSequenceTests(unittest.TestCase):
    """Verify the Homebridge-compatible close-apps sequence."""

    def test_sequence_shape(self) -> None:
        sequence = HELPERS.build_close_apps_sequence(5)
        self.assertEqual(sequence[:3], (("home", 0.1), ("home", 0.8), ("left", 0.3)))
        self.assertEqual(sequence[-1], ("home", 0.0))
        self.assertEqual(len(sequence), 14)

    def test_count_is_clamped(self) -> None:
        self.assertEqual(HELPERS.clamp_close_apps_count(1), 5)
        self.assertEqual(HELPERS.clamp_close_apps_count(99), 35)
        self.assertEqual(HELPERS.clamp_close_apps_count("bad"), 15)


if __name__ == "__main__":
    unittest.main()
