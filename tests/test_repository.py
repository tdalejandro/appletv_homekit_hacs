"""Repository-level validation tests."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "appletv_homekit_hacs"


class RepositoryTests(unittest.TestCase):
    """Validate HACS and Home Assistant metadata."""

    def test_required_files_exist(self) -> None:
        required = (
            ROOT / "hacs.json",
            INTEGRATION / "manifest.json",
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
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertIn("apple_tv", manifest["dependencies"])
        self.assertIn("homekit", manifest["dependencies"])


if __name__ == "__main__":
    unittest.main()
