import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "publish_release.py"
SPEC = importlib.util.spec_from_file_location("publish_release", SCRIPT)
publish_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publish_release)


class CatalogVisibilityTests(unittest.TestCase):
    def test_mods_are_listed_by_default(self):
        known = {}
        self.assertTrue(publish_release.should_index_mod(known, "ruby", {}))
        self.assertEqual(known, {})

    def test_disabled_mod_is_removed_from_existing_catalog(self):
        known = {"vex_sentinel": {"id": "vex_sentinel"}}
        metadata = {"catalog_enabled": False}
        self.assertFalse(publish_release.should_index_mod(known, "vex_sentinel", metadata))
        self.assertNotIn("vex_sentinel", known)

    def test_catalog_enabled_must_be_boolean(self):
        for value in (None, 0, "false"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                publish_release.should_index_mod({}, "ruby", {"catalog_enabled": value})


if __name__ == "__main__":
    unittest.main()
