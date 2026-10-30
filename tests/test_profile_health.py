"""Tests for AF-03: Profile Health Check."""
import os
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.profile_health import (
    Finding, Severity, check_profile, check_all_profiles,
)


class ProfileHealthTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profiles_dir = Path(self.tmp) / "profiles"
        self.profiles_dir.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_profile(self, name: str, *, storage: bool = True,
                      cache: bool = True) -> Path:
        p = self.profiles_dir / name
        p.mkdir()
        if storage:
            (p / "storage").mkdir()
        if cache:
            (p / "cache").mkdir()
        return p

    def test_healthy_profile(self):
        self._make_profile("good")
        findings = check_profile(self.profiles_dir / "good", "good")
        self.assertEqual(len(findings), 0)

    def test_missing_directory(self):
        findings = check_profile(self.profiles_dir / "nope", "nope")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, Severity.ERROR)
        self.assertEqual(findings[0].code, "DIR_MISSING")

    def test_missing_storage_warning(self):
        self._make_profile("nostor", storage=False)
        findings = check_profile(self.profiles_dir / "nostor", "nostor")
        codes = [f.code for f in findings]
        self.assertIn("STORAGE_MISSING", codes)

    def test_missing_cache_info(self):
        self._make_profile("nocache", cache=False)
        findings = check_profile(self.profiles_dir / "nocache", "nocache")
        codes = [f.code for f in findings]
        self.assertIn("CACHE_MISSING", codes)
        # cache missing is info, not error
        for f in findings:
            if f.code == "CACHE_MISSING":
                self.assertEqual(f.severity, Severity.INFO)

    def test_symlink_detection(self):
        p = self._make_profile("sym")
        target = p / "storage" / "real_file"
        target.write_text("data")
        link = p / "storage" / "sneaky_link"
        link.symlink_to(target)
        findings = check_profile(p, "sym")
        codes = [f.code for f in findings]
        self.assertIn("SYMLINK_FOUND", codes)

    def test_size_exceeded(self):
        p = self._make_profile("big")
        # Write a file just over 1 KiB, set limit to 1 KiB
        (p / "storage" / "data.bin").write_bytes(b"x" * 2000)
        findings = check_profile(p, "big", max_bytes=1024)
        codes = [f.code for f in findings]
        self.assertIn("SIZE_EXCEEDED", codes)

    def test_corrupt_cookie_db(self):
        p = self._make_profile("badcookie")
        cookies = p / "storage" / "Cookies"
        cookies.write_bytes(b"NOT SQLITE AT ALL")
        findings = check_profile(p, "badcookie")
        codes = [f.code for f in findings]
        self.assertIn("COOKIE_CORRUPT", codes)

    def test_valid_cookie_db(self):
        p = self._make_profile("goodcookie")
        cookies = p / "storage" / "Cookies"
        # Write valid SQLite header
        cookies.write_bytes(b"SQLite format 3\x00" + b"\x00" * 84)
        findings = check_profile(p, "goodcookie")
        codes = [f.code for f in findings]
        self.assertNotIn("COOKIE_CORRUPT", codes)

    def test_check_all_profiles(self):
        self._make_profile("alpha")
        self._make_profile("beta", storage=False)
        findings = check_all_profiles(self.profiles_dir)
        profiles = {f.profile for f in findings}
        self.assertIn("beta", profiles)

    def test_no_profiles_dir(self):
        findings = check_all_profiles(Path(self.tmp) / "nonexistent")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "PROFILES_DIR_MISSING")

    def test_all_healthy_returns_all_ok(self):
        self._make_profile("perfect")
        findings = check_all_profiles(self.profiles_dir)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].code, "ALL_OK")


if __name__ == "__main__":
    unittest.main()
