"""AF-15 profile dashboard directory discovery regression tests."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.profile_listing import list_profiles


class ProfileListingTests(unittest.TestCase):
    def test_missing_root_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list_profiles(Path(tmp) / "absent"), [])

    def test_only_valid_directories_returned_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("Bravo", "alpha", "Profile_02", ".hidden", "bad name"):
                (root / name).mkdir()
            (root / "file.txt").write_text("not a profile")
            (root / "linked").symlink_to(root / "alpha", target_is_directory=True)
            self.assertEqual(list_profiles(root), ["Bravo", "Profile_02", "alpha"])

    def test_does_not_create_or_change_profile_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Existing").mkdir()
            before = sorted(str(p) for p in root.iterdir())
            self.assertEqual(list_profiles(root), ["Existing"])
            self.assertEqual(sorted(str(p) for p in root.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
