"""Tests for AF-07: Profile Import, Export and Clone."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.backup import _encrypt, _decrypt

try:
    from devseatech_browser.profile_migration import (
        export_profile, import_profile, clone_profile, list_profiles,
    )
    from devseatech_browser.backup import _derive_key
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class ProfileMigrationPureTests(unittest.TestCase):
    """Tests that work without cryptography."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profiles_dir = Path(self.tmp) / "profiles"
        self.profiles_dir.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_list_profiles_empty(self):
        from devseatech_browser.profile_migration import list_profiles
        self.assertEqual(list_profiles(self.profiles_dir), [])

    def test_list_profiles(self):
        from devseatech_browser.profile_migration import list_profiles
        (self.profiles_dir / "alpha").mkdir()
        (self.profiles_dir / "beta").mkdir()
        (self.profiles_dir / ".hidden").mkdir()
        self.assertEqual(list_profiles(self.profiles_dir), ["alpha", "beta"])

    def test_clone_source_missing(self):
        from devseatech_browser.profile_migration import clone_profile
        with self.assertRaises(RuntimeError):
            clone_profile(self.profiles_dir, "nope", "copy")

    def test_clone_target_exists(self):
        from devseatech_browser.profile_migration import clone_profile
        (self.profiles_dir / "src").mkdir()
        (self.profiles_dir / "dst").mkdir()
        with self.assertRaises(RuntimeError):
            clone_profile(self.profiles_dir, "src", "dst")

    def test_clone_profile(self):
        from devseatech_browser.profile_migration import clone_profile
        src = self.profiles_dir / "original"
        (src / "storage").mkdir(parents=True)
        (src / "storage" / "data.txt").write_text("hello")
        (src / "cache").mkdir()
        (src / "cache" / "tmp.bin").write_bytes(b"x")

        result = clone_profile(self.profiles_dir, "original", "cloned")
        self.assertTrue(result.is_dir())
        self.assertTrue((result / "storage" / "data.txt").exists())
        # Cache should be excluded
        self.assertFalse((result / "cache" / "tmp.bin").exists())


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class ProfileExportImportTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profiles_dir = Path(self.tmp) / "profiles"
        self.profiles_dir.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_export_import_roundtrip(self):
        # Create a profile with data
        src = self.profiles_dir / "test_profile"
        (src / "storage").mkdir(parents=True)
        (src / "storage" / "cookies.db").write_text("fake cookies")
        (src / "cache").mkdir()
        (src / "cache" / "temp.bin").write_bytes(b"cache data")

        archive = Path(self.tmp) / "export.enc"
        export_profile(src, "password123", archive)
        self.assertTrue(archive.exists())

        # Import into new profile
        result = import_profile(archive, "password123",
                                self.profiles_dir, "imported")
        self.assertTrue(result.is_dir())
        self.assertTrue((result / "storage" / "cookies.db").exists())

    def test_import_wrong_password(self):
        src = self.profiles_dir / "p"
        (src / "storage").mkdir(parents=True)
        (src / "storage" / "f.txt").write_text("data")
        archive = Path(self.tmp) / "e.enc"
        export_profile(src, "right", archive)

        with self.assertRaises(ValueError):
            import_profile(archive, "wrong", self.profiles_dir, "new")

    def test_import_existing_name_fails(self):
        src = self.profiles_dir / "existing"
        (src / "storage").mkdir(parents=True)
        archive = Path(self.tmp) / "e.enc"
        export_profile(src, "pass", archive)

        with self.assertRaises(RuntimeError):
            import_profile(archive, "pass", self.profiles_dir, "existing")

    def test_export_missing_profile(self):
        with self.assertRaises(RuntimeError):
            export_profile(self.profiles_dir / "nope", "pass",
                           Path(self.tmp) / "out.enc")


if __name__ == "__main__":
    unittest.main()
