"""Tests for AF-16: Keyboard Shortcuts Manager."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.keyboard_shortcuts import (
    ShortcutStore, DEFAULT_SHORTCUTS,
)


class ShortcutStoreTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"
        self.profile.mkdir()
        self.store = ShortcutStore(self.profile)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_defaults_loaded(self):
        self.assertGreater(self.store.count(), 0)
        sc = self.store.get("new_tab")
        self.assertIsNotNone(sc)
        self.assertEqual(sc.keys, "Ctrl+T")

    def test_set_custom_keys(self):
        self.store.set_keys("new_tab", "Ctrl+N")
        sc = self.store.get("new_tab")
        self.assertEqual(sc.keys, "Ctrl+N")
        self.assertTrue(sc.custom)

    def test_persistence(self):
        self.store.set_keys("new_tab", "Ctrl+N")
        store2 = ShortcutStore(self.profile)
        sc = store2.get("new_tab")
        self.assertEqual(sc.keys, "Ctrl+N")

    def test_reset_action(self):
        self.store.set_keys("new_tab", "Ctrl+N")
        self.assertTrue(self.store.reset("new_tab"))
        sc = self.store.get("new_tab")
        self.assertEqual(sc.keys, "Ctrl+T")

    def test_reset_all(self):
        self.store.set_keys("new_tab", "Ctrl+N")
        self.store.reset_all()
        sc = self.store.get("new_tab")
        self.assertEqual(sc.keys, "Ctrl+T")
        self.assertFalse(sc.custom)

    def test_conflict_detection(self):
        self.store.set_keys("close_tab", "Ctrl+T")  # same as new_tab
        conflicts = self.store.validate()
        self.assertGreater(len(conflicts), 0)
        keys_with_conflicts = [c.keys for c in conflicts]
        self.assertTrue(any("ctrl+t" in k for k in keys_with_conflicts))

    def test_no_conflicts_default(self):
        conflicts = self.store.validate()
        self.assertEqual(len(conflicts), 0)

    def test_find_by_keys(self):
        results = self.store.find_by_keys("Ctrl+T")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].action, "new_tab")

    def test_list_enabled(self):
        enabled = self.store.list_enabled()
        self.assertEqual(len(enabled), self.store.count())


if __name__ == "__main__":
    unittest.main()
