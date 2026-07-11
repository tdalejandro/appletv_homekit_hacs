"""Repository-level validation tests."""

import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "appletv_homekit_hacs"


class RepositoryTests(unittest.TestCase):
    """Validate HACS and Home Assistant metadata."""

    def test_required_files_exist(self) -> None:
        required = (
            ROOT / "hacs.json",
            INTEGRATION / "manifest.json",
            INTEGRATION / "brand" / "icon.png",
            INTEGRATION / "brand" / "icon@2x.png",
            INTEGRATION / "strings.json",
            INTEGRATION / "translations" / "es.json",
        )
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_json_files_parse(self) -> None:
        for path in ROOT.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_manifest_identity(self) -> None:
        manifest = json.loads(
            (INTEGRATION / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["domain"], "appletv_homekit_hacs")
        self.assertEqual(manifest["version"], "0.2.1")
        self.assertIn("apple_tv", manifest["dependencies"])
        self.assertIn("homekit", manifest["dependencies"])

    def test_brand_images_match_home_assistant_dimensions(self) -> None:
        expected_dimensions = {
            "icon.png": (256, 256),
            "icon@2x.png": (512, 512),
        }
        brand = INTEGRATION / "brand"
        for filename, dimensions in expected_dimensions.items():
            with self.subTest(filename=filename):
                image = (brand / filename).read_bytes()
                self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(
                    struct.unpack(">II", image[16:24]), dimensions
                )


if __name__ == "__main__":
    unittest.main()
