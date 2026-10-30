"""Tests for AF-15: Workspace and Group Management."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.workspace_manager import WorkspaceStore


class WorkspaceStoreTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.store = WorkspaceStore(Path(self.tmp))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create(self):
        ws = self.store.create("Dev", description="Development")
        self.assertEqual(ws.name, "Dev")
        self.assertEqual(self.store.count(), 1)

    def test_create_duplicate_raises(self):
        self.store.create("Dev")
        with self.assertRaises(ValueError):
            self.store.create("Dev")

    def test_create_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.store.create("")

    def test_get(self):
        self.store.create("Test")
        ws = self.store.get("Test")
        self.assertIsNotNone(ws)
        self.assertIsNone(self.store.get("Nope"))

    def test_delete(self):
        self.store.create("Gone")
        self.assertTrue(self.store.delete("Gone"))
        self.assertFalse(self.store.delete("Gone"))

    def test_persistence(self):
        self.store.create("Persist", tags=["work"])
        store2 = WorkspaceStore(Path(self.tmp))
        ws = store2.get("Persist")
        self.assertIsNotNone(ws)
        self.assertIn("work", ws.tags)

    def test_search_by_name(self):
        self.store.create("Development")
        self.store.create("Production")
        results = self.store.search("dev")
        self.assertEqual(len(results), 1)

    def test_search_by_tag(self):
        self.store.create("W1", tags=["frontend"])
        self.store.create("W2", tags=["backend"])
        results = self.store.search("front")
        self.assertEqual(len(results), 1)

    def test_add_profile(self):
        self.store.create("Dev")
        self.assertTrue(self.store.add_profile("Dev", "profile1"))
        ws = self.store.get("Dev")
        self.assertIn("profile1", ws.profiles)

    def test_remove_profile(self):
        self.store.create("Dev", profiles=["p1", "p2"])
        self.assertTrue(self.store.remove_profile("Dev", "p1"))
        ws = self.store.get("Dev")
        self.assertNotIn("p1", ws.profiles)

    def test_find_by_profile(self):
        self.store.create("A", profiles=["shared"])
        self.store.create("B", profiles=["shared", "other"])
        self.store.create("C", profiles=["other"])
        results = self.store.find_by_profile("shared")
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
