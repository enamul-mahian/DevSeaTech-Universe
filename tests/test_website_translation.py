"""Tests for AF-17: Website Translation."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.website_translation import (
    TranslationConfig, save_config, load_config,
    is_site_excluded, needs_privacy_disclosure, get_supported_languages,
)


class TranslationConfigTests(unittest.TestCase):

    def test_defaults(self):
        c = TranslationConfig()
        self.assertFalse(c.enabled)
        self.assertEqual(c.target_language, "")

    def test_roundtrip(self):
        c = TranslationConfig(enabled=True, target_language="bn",
                              excluded_sites=["localhost"])
        d = c.to_dict()
        c2 = TranslationConfig.from_dict(d)
        self.assertTrue(c2.enabled)
        self.assertEqual(c2.target_language, "bn")

    def test_site_excluded(self):
        c = TranslationConfig(excluded_sites=["example.com"])
        self.assertTrue(is_site_excluded(c, "https://example.com/page"))
        self.assertFalse(is_site_excluded(c, "https://other.com"))

    def test_privacy_disclosure_needed(self):
        c = TranslationConfig(enabled=True, privacy_acknowledged=False)
        self.assertTrue(needs_privacy_disclosure(c))
        c2 = TranslationConfig(enabled=True, privacy_acknowledged=True)
        self.assertFalse(needs_privacy_disclosure(c2))

    def test_supported_languages(self):
        langs = get_supported_languages()
        self.assertGreater(len(langs), 5)
        codes = [l["code"] for l in langs]
        self.assertIn("bn", codes)


class TranslationPersistenceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"
        self.profile.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_load(self):
        c = TranslationConfig(enabled=True, target_language="es")
        save_config(self.profile, c)
        loaded = load_config(self.profile)
        self.assertTrue(loaded.enabled)
        self.assertEqual(loaded.target_language, "es")

    def test_load_missing(self):
        c = load_config(self.profile)
        self.assertFalse(c.enabled)


if __name__ == "__main__":
    unittest.main()
