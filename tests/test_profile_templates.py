"""Tests for AF-11: Profile Templates."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.profile_templates import (
    TemplateConfig, BLOCKED_FIELDS,
    save_template, load_template, list_templates,
    delete_template, apply_template, _slugify,
)


class TemplateConfigTests(unittest.TestCase):

    def test_blocked_fields_stripped(self):
        tc = TemplateConfig(name="test",
                            custom_settings={"cookies": "bad", "theme": "dark"})
        d = tc.to_dict()
        self.assertNotIn("cookies", d["custom_settings"])
        self.assertIn("theme", d["custom_settings"])

    def test_from_dict_strips_blocked(self):
        data = {"name": "x", "custom_settings": {"passwords": "no", "zoom": 2}}
        tc = TemplateConfig.from_dict(data)
        self.assertNotIn("passwords", tc.custom_settings)
        self.assertIn("zoom", tc.custom_settings)

    def test_roundtrip(self):
        tc = TemplateConfig(name="Dev", homepage="https://dev.to",
                            search_engine="ddg", zoom_level=1.25)
        d = tc.to_dict()
        tc2 = TemplateConfig.from_dict(d)
        self.assertEqual(tc2.name, "Dev")
        self.assertEqual(tc2.zoom_level, 1.25)


class TemplatePersistenceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_load(self):
        tc = TemplateConfig(name="Work", homepage="https://work.com")
        save_template(self.app_dir, tc)
        loaded = load_template(self.app_dir, "Work")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.homepage, "https://work.com")

    def test_list_templates(self):
        save_template(self.app_dir, TemplateConfig(name="Alpha"))
        save_template(self.app_dir, TemplateConfig(name="Beta"))
        names = list_templates(self.app_dir)
        self.assertEqual(names, ["alpha", "beta"])

    def test_list_empty(self):
        self.assertEqual(list_templates(self.app_dir), [])

    def test_delete_template(self):
        save_template(self.app_dir, TemplateConfig(name="gone"))
        self.assertTrue(delete_template(self.app_dir, "gone"))
        self.assertIsNone(load_template(self.app_dir, "gone"))

    def test_delete_missing(self):
        self.assertFalse(delete_template(self.app_dir, "nope"))

    def test_load_missing(self):
        self.assertIsNone(load_template(self.app_dir, "nope"))

    def test_save_empty_name_raises(self):
        with self.assertRaises(ValueError):
            save_template(self.app_dir, TemplateConfig(name=""))


class ApplyTemplateTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_apply_creates_settings(self):
        tc = TemplateConfig(name="Dev", homepage="https://dev.to")
        path = apply_template(tc, self.profile)
        self.assertTrue(path.exists())
        import json
        data = json.loads(path.read_text())
        self.assertEqual(data["homepage"], "https://dev.to")
        self.assertEqual(data["applied_template"], "Dev")


class SlugifyTests(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(_slugify("My Template"), "my-template")

    def test_special_chars(self):
        self.assertEqual(_slugify("test@#$!"), "test")

    def test_empty(self):
        self.assertEqual(_slugify(""), "template")


if __name__ == "__main__":
    unittest.main()
