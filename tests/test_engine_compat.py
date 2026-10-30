"""Tests for AF-04: Engine Compatibility Checker."""
import json
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.engine_compat import (
    CheckResult, CompatCheck, check_python_version, check_platform,
    check_disk_space, check_storage_schema, run_all_checks,
    is_compatible, format_report,
)


class EngineCompatTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_python_version_ok(self):
        r = check_python_version()
        self.assertEqual(r.result, CheckResult.OK)

    def test_platform_check(self):
        r = check_platform()
        # should be OK on Linux (CI) or Windows
        self.assertIn(r.result, (CheckResult.OK, CheckResult.WARNING))

    def test_disk_space_ok(self):
        r = check_disk_space(self.app_dir)
        self.assertIn(r.result, (CheckResult.OK, CheckResult.WARNING))

    def test_storage_schema_first_run(self):
        r = check_storage_schema(self.app_dir)
        self.assertEqual(r.result, CheckResult.OK)
        self.assertIn("First run", r.detail)

    def test_storage_schema_valid(self):
        auth = self.app_dir / "auth.json"
        auth.write_text(json.dumps({"master": {}, "admin": {}}))
        r = check_storage_schema(self.app_dir)
        self.assertEqual(r.result, CheckResult.OK)

    def test_storage_schema_missing_keys(self):
        auth = self.app_dir / "auth.json"
        auth.write_text(json.dumps({"master": {}}))
        r = check_storage_schema(self.app_dir)
        self.assertEqual(r.result, CheckResult.WARNING)
        self.assertIn("admin", r.detail)

    def test_storage_schema_corrupt(self):
        auth = self.app_dir / "auth.json"
        auth.write_text("NOT JSON")
        r = check_storage_schema(self.app_dir)
        self.assertEqual(r.result, CheckResult.FAIL)

    def test_run_all_checks(self):
        checks = run_all_checks(self.app_dir)
        self.assertGreaterEqual(len(checks), 7)

    def test_is_compatible_all_ok(self):
        checks = [CompatCheck("A", CheckResult.OK, "fine"),
                  CompatCheck("B", CheckResult.WARNING, "meh")]
        self.assertTrue(is_compatible(checks))

    def test_is_compatible_with_fail(self):
        checks = [CompatCheck("A", CheckResult.OK, "fine"),
                  CompatCheck("B", CheckResult.FAIL, "bad")]
        self.assertFalse(is_compatible(checks))

    def test_format_report(self):
        checks = [CompatCheck("Test", CheckResult.OK, "good")]
        report = format_report(checks)
        self.assertIn("Test", report)
        self.assertIn("good", report)


if __name__ == "__main__":
    unittest.main()
