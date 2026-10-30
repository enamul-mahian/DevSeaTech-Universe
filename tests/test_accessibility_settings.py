"""Tests for AF-18: Accessibility Settings."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.accessibility_settings import (
    AccessibilityConfig, save_config, load_config,
    get_preset, list_presets,
)


class AccessibilityConfigTests(unittest.TestCase):

    def test_defaults(self):
        c = AccessibilityConfig()
        self.assertFalse(c.high_contrast)
        self.assertEqual(c.font_scale, 1.0)
        self.assertTrue(c.keyboard_navigation)

    def test_roundtrip(self):
        c = AccessibilityConfig(high_contrast=True, font_scale=1.5)
        d = c.to_dict()
        c2 = AccessibilityConfig.from_dict(d)
        self.assertTrue(c2.high_contrast)
        self.assertEqual(c2.font_scale, 1.5)

    def test_validate_ok(self):
        c = AccessibilityConfig(font_scale=1.5)
        self.assertEqual(c.validate(), [])

    def test_validate_bad_scale(self):
        c = AccessibilityConfig(font_scale=5.0)
        issues = c.validate()
        self.assertTrue(len(issues) > 0)

    def test_presets(self):
        names = list_presets()
        self.assertIn("high_visibility", names)
        preset = get_preset("high_visibility")
        self.assertIsNotNone(preset)
        self.assertTrue(preset.high_contrast)

    def test_preset_missing(self):
        self.assertIsNone(get_preset("nonexistent"))

    def test_screen_reader_preset(self):
        p = get_preset("screen_reader")
        self.assertTrue(p.screen_reader_mode)
        self.assertTrue(p.keyboard_navigation)


class AccessibilityPersistenceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"
        self.profile.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_load(self):
        c = AccessibilityConfig(high_contrast=True, font_scale=2.0)
        save_config(self.profile, c)
        loaded = load_config(self.profile)
        self.assertTrue(loaded.high_contrast)
        self.assertEqual(loaded.font_scale, 2.0)

    def test_load_missing(self):
        c = load_config(self.profile)
        self.assertFalse(c.high_contrast)


if __name__ == "__main__":
    unittest.main()
