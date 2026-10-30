"""Tests for AF-01: Crash Recovery & Session Restore."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.session_restore import (
    TabEntry, save_session, mark_clean, load_session, needs_restore,
)


class SessionRestoreTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_session_file_returns_none(self):
        self.assertIsNone(load_session(self.app_dir))
        self.assertFalse(needs_restore(self.app_dir))

    def test_save_and_load_unclean(self):
        tabs = [
            TabEntry(profile="Work", url="https://example.com", title="Example"),
            TabEntry(profile="Default", url="https://google.com"),
        ]
        save_session(self.app_dir, tabs)
        self.assertTrue(needs_restore(self.app_dir))
        restored = load_session(self.app_dir)
        self.assertIsNotNone(restored)
        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0].profile, "Work")
        self.assertEqual(restored[0].url, "https://example.com")
        self.assertEqual(restored[1].profile, "Default")

    def test_mark_clean_clears_restore(self):
        save_session(self.app_dir, [TabEntry("A", "https://a.com")])
        self.assertTrue(needs_restore(self.app_dir))
        mark_clean(self.app_dir)
        self.assertFalse(needs_restore(self.app_dir))
        self.assertIsNone(load_session(self.app_dir))

    def test_corrupt_file_returns_none(self):
        path = self.app_dir / "session.json"
        path.write_text("NOT JSON", encoding="utf-8")
        self.assertIsNone(load_session(self.app_dir))

    def test_empty_tabs_returns_none(self):
        save_session(self.app_dir, [])
        self.assertIsNone(load_session(self.app_dir))

    def test_skips_entries_missing_profile_or_url(self):
        path = self.app_dir / "session.json"
        data = {"clean": False, "tabs": [
            {"profile": "X", "url": ""},  # empty url → skip
            {"profile": "", "url": "https://a.com"},  # empty profile → skip
            {"profile": "Y", "url": "https://b.com"},  # valid
        ]}
        path.write_text(json.dumps(data), encoding="utf-8")
        result = load_session(self.app_dir)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].profile, "Y")

    def test_atomic_write_permissions(self):
        save_session(self.app_dir, [TabEntry("P", "https://x.com")])
        path = self.app_dir / "session.json"
        mode = os.stat(path).st_mode & 0o777
        self.assertEqual(mode, 0o600)

    def test_overwrite_updates_state(self):
        save_session(self.app_dir, [TabEntry("A", "https://a.com")])
        save_session(self.app_dir, [TabEntry("B", "https://b.com")])
        restored = load_session(self.app_dir)
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored[0].profile, "B")


if __name__ == "__main__":
    unittest.main()
