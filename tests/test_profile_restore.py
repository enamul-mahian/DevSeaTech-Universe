"""Tests for safe restore into a new profile."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from devseatech_browser.profile_restore import restore_as_new_profile


class RestoreNewProfileTests(unittest.TestCase):
    def test_restores_only_into_new_profile(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            bundle = base / "test.dstbak"
            bundle.write_bytes(b"encrypted")
            profiles = base / "profiles"
            def restore(_backup, _pass, target):
                (target / "data.json").write_text("restored")
            with patch("devseatech_browser.profile_restore.restore_backup", side_effect=restore):
                target = restore_as_new_profile(bundle, "secret", profiles, "Profile_2")
            self.assertEqual((target / "data.json").read_text(), "restored")

    def test_existing_profile_remains_untouched(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            bundle = base / "test.dstbak"
            bundle.write_bytes(b"encrypted")
            profiles = base / "profiles"
            target = profiles / "Existing"
            target.mkdir(parents=True)
            (target / "keep.txt").write_text("original")
            with self.assertRaises(FileExistsError):
                restore_as_new_profile(bundle, "secret", profiles, "Existing")
            self.assertEqual((target / "keep.txt").read_text(), "original")

    def test_failed_restore_removes_staging(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            bundle = base / "test.dstbak"
            bundle.write_bytes(b"encrypted")
            profiles = base / "profiles"
            with patch("devseatech_browser.profile_restore.restore_backup",
                       side_effect=ValueError("invalid key")):
                with self.assertRaises(ValueError):
                    restore_as_new_profile(bundle, "wrong", profiles, "New")
            self.assertEqual(list(profiles.iterdir()), [])

    def test_invalid_names_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            bundle = Path(root) / "test.dstbak"
            bundle.write_bytes(b"encrypted")
            for name in ("../escape", "", "bad name", "x" * 41, "folder/name", "C:"):
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        restore_as_new_profile(bundle, "pass", Path(root) / "profiles", name)


if __name__ == "__main__":
    unittest.main()
