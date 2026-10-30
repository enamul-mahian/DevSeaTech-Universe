"""Tests for AF-12: Permission Manager."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.permission_manager import (
    Permission, PermissionDecision, PermissionStore,
)


class PermissionStoreTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"
        self.profile.mkdir()
        self.store = PermissionStore(self.profile)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_is_ask(self):
        d = self.store.get_decision("https://ex.com", Permission.CAMERA)
        self.assertEqual(d, PermissionDecision.ASK)

    def test_set_and_get(self):
        self.store.set_permission("https://ex.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        d = self.store.get_decision("https://ex.com", Permission.CAMERA)
        self.assertEqual(d, PermissionDecision.ALLOW)

    def test_deny(self):
        self.store.set_permission("https://ex.com", Permission.GEOLOCATION,
                                  PermissionDecision.DENY)
        d = self.store.get_decision("https://ex.com", Permission.GEOLOCATION)
        self.assertEqual(d, PermissionDecision.DENY)

    def test_persistence(self):
        self.store.set_permission("https://a.com", Permission.MICROPHONE,
                                  PermissionDecision.ALLOW)
        store2 = PermissionStore(self.profile)
        d = store2.get_decision("https://a.com", Permission.MICROPHONE)
        self.assertEqual(d, PermissionDecision.ALLOW)

    def test_list_for_origin(self):
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        self.store.set_permission("https://a.com", Permission.NOTIFICATIONS,
                                  PermissionDecision.DENY)
        self.store.set_permission("https://b.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        entries = self.store.list_for_origin("https://a.com")
        self.assertEqual(len(entries), 2)

    def test_list_origins(self):
        self.store.set_permission("https://b.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.DENY)
        self.assertEqual(self.store.list_origins(),
                         ["https://a.com", "https://b.com"])

    def test_remove(self):
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        self.assertTrue(self.store.remove("https://a.com", Permission.CAMERA))
        self.assertEqual(self.store.get_decision("https://a.com",
                         Permission.CAMERA), PermissionDecision.ASK)

    def test_remove_missing(self):
        self.assertFalse(self.store.remove("https://x.com", Permission.CAMERA))

    def test_clear_origin(self):
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        self.store.set_permission("https://a.com", Permission.MICROPHONE,
                                  PermissionDecision.DENY)
        removed = self.store.clear_origin("https://a.com")
        self.assertEqual(removed, 2)
        self.assertEqual(self.store.count(), 0)

    def test_count(self):
        self.assertEqual(self.store.count(), 0)
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW)
        self.assertEqual(self.store.count(), 1)

    def test_get_entry(self):
        self.store.set_permission("https://a.com", Permission.CAMERA,
                                  PermissionDecision.ALLOW, "admin")
        entry = self.store.get_entry("https://a.com", Permission.CAMERA)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.decided_by, "admin")


if __name__ == "__main__":
    unittest.main()
