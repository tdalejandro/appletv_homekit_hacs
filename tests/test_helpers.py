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


if __name__ == "__main__":
    unittest.main()

