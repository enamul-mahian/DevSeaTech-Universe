"""Tests for AF-14: Browser Diagnostics and Repair."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.browser_diagnostics import (
    DiagStatus, run_diagnostics, format_diagnostics, apply_repair,
)


class DiagnosticsTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_basic_diagnostics(self):
        findings = run_diagnostics(self.app_dir)
        self.assertTrue(len(findings) >= 4)

    def test_app_dir_ok(self):
        findings = run_diagnostics(self.app_dir)
        app_check = [f for f in findings if f.name == "app_directory"][0]
        self.assertEqual(app_check.status, DiagStatus.OK)

    def test_missing_profiles_warning(self):
        findings = run_diagnostics(self.app_dir)
        prof = [f for f in findings if f.name == "profiles_directory"][0]
        self.assertEqual(prof.status, DiagStatus.WARNING)
        self.assertTrue(prof.repairable)

    def test_profiles_exist(self):
        (self.app_dir / "profiles" / "default").mkdir(parents=True)
        findings = run_diagnostics(self.app_dir)
        prof = [f for f in findings if f.name == "profiles_directory"][0]
        self.assertEqual(prof.status, DiagStatus.OK)

    def test_invalid_settings(self):
        (self.app_dir / "settings.json").write_text("{bad")
        findings = run_diagnostics(self.app_dir)
        s = [f for f in findings if f.name == "settings_file"][0]
        self.assertEqual(s.status, DiagStatus.ERROR)
        self.assertTrue(s.repairable)

    def test_temp_files_detected(self):
        (self.app_dir / "orphan.tmp").write_text("x")
        findings = run_diagnostics(self.app_dir)
        t = [f for f in findings if f.name == "temp_files"][0]
        self.assertEqual(t.status, DiagStatus.WARNING)

    def test_format_output(self):
        findings = run_diagnostics(self.app_dir)
        report = format_diagnostics(findings)
        self.assertIn("Browser Diagnostics", report)


class RepairTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_repair_requires_confirmation(self):
        r = apply_repair(self.app_dir, "create_profiles_dir", confirmed=False)
        self.assertFalse(r.success)

    def test_create_profiles_dir(self):
        r = apply_repair(self.app_dir, "create_profiles_dir", confirmed=True)
        self.assertTrue(r.success)
        self.assertTrue((self.app_dir / "profiles").is_dir())

    def test_reset_settings_with_backup(self):
        (self.app_dir / "settings.json").write_text("{bad")
        r = apply_repair(self.app_dir, "reset_settings", confirmed=True)
        self.assertTrue(r.success)
        self.assertIn("{}", (self.app_dir / "settings.json").read_text())
        self.assertTrue(r.backup_path)

    def test_clean_temps(self):
        (self.app_dir / "a.tmp").write_text("x")
        (self.app_dir / "b.tmp").write_text("y")
        r = apply_repair(self.app_dir, "clean_temps", confirmed=True)
        self.assertTrue(r.success)
        self.assertIn("2", r.message)

    def test_unknown_repair(self):
        r = apply_repair(self.app_dir, "nonexistent", confirmed=True)
        self.assertFalse(r.success)


if __name__ == "__main__":
    unittest.main()
