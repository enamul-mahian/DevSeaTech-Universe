"""Local preview recovery tests: no real user data is accessed."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.recovery import archive_preview_auth


class PreviewRecoveryTests(unittest.TestCase):
    def test_wrong_confirmation_preserves_auth_and_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "auth.json").write_text("test-auth")
            (root / "profiles").mkdir()
            (root / "profiles" / "marker").write_text("keep-me")
            with self.assertRaises(ValueError):
                archive_preview_auth(root, "NO")
            self.assertTrue((root / "auth.json").exists())
            self.assertEqual((root / "profiles" / "marker").read_text(), "keep-me")

    def test_archives_auth_and_preserves_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "auth.json").write_text("test-auth")
            (root / "profiles").mkdir()
            (root / "profiles" / "marker").write_text("keep-me")
            backup = archive_preview_auth(root, "RESET DEVELOPMENT PREVIEW LOGIN")
            self.assertFalse((root / "auth.json").exists())
            self.assertEqual(backup.read_text(), "test-auth")
            self.assertEqual((root / "profiles" / "marker").read_text(), "keep-me")


if __name__ == "__main__":
    unittest.main()
