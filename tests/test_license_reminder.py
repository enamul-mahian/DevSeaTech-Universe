"""Tests for AF-10: License Renewal Reminder."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.license_reminder import (
    AlertLevel, LicenseInfo, LicensePlan,
    check_renewal_needed, save_license_info, load_license_info,
)


class LicenseInfoTests(unittest.TestCase):

    def test_duration_hours(self):
        info = LicenseInfo(LicensePlan.STANDARD, 0.0, 720 * 3600.0)
        self.assertAlmostEqual(info.duration_hours, 720.0)

    def test_is_trial(self):
        self.assertTrue(LicenseInfo(LicensePlan.TRIAL_24H, 0, 1).is_trial)
        self.assertTrue(LicenseInfo(LicensePlan.TRIAL_72H, 0, 1).is_trial)
        self.assertFalse(LicenseInfo(LicensePlan.STANDARD, 0, 1).is_trial)


class RenewalCheckTests(unittest.TestCase):

    def _std_license(self, remaining_hours: float) -> LicenseInfo:
        now = 1_000_000.0
        return LicenseInfo(LicensePlan.STANDARD, now - 3600,
                           now + remaining_hours * 3600)

    def test_plenty_of_time(self):
        info = self._std_license(500)  # 500 hours left
        alert = check_renewal_needed(info, server_time=1_000_000.0)
        self.assertIsNone(alert)

    def test_notice_level(self):
        info = self._std_license(100)  # ~4 days
        alert = check_renewal_needed(info, server_time=1_000_000.0)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.level, AlertLevel.NOTICE)

    def test_warning_level(self):
        info = self._std_license(48)  # 2 days
        alert = check_renewal_needed(info, server_time=1_000_000.0)
        self.assertEqual(alert.level, AlertLevel.WARNING)

    def test_urgent_level(self):
        info = self._std_license(10)  # 10 hours
        alert = check_renewal_needed(info, server_time=1_000_000.0)
        self.assertEqual(alert.level, AlertLevel.URGENT)

    def test_expired(self):
        info = self._std_license(-1)  # 1 hour past
        alert = check_renewal_needed(info, server_time=1_000_000.0)
        self.assertEqual(alert.level, AlertLevel.EXPIRED)
        self.assertIn("expired", alert.message)

    def test_trial_thresholds(self):
        now = 1_000_000.0
        info = LicenseInfo(LicensePlan.TRIAL_24H, now - 3600,
                           now + 0.5 * 3600)  # 30 min left
        alert = check_renewal_needed(info, server_time=now)
        self.assertEqual(alert.level, AlertLevel.URGENT)
        self.assertIn("trial", alert.message)


class PersistenceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_load_roundtrip(self):
        info = LicenseInfo(LicensePlan.STANDARD, 1000.0, 2000.0,
                           "dev-123", "key-abc")
        save_license_info(Path(self.tmp), info)
        loaded = load_license_info(Path(self.tmp))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.plan, LicensePlan.STANDARD)
        self.assertEqual(loaded.device_id, "dev-123")

    def test_load_missing(self):
        self.assertIsNone(load_license_info(Path(self.tmp)))

    def test_load_corrupt(self):
        (Path(self.tmp) / "license_state.json").write_text("{bad json")
        self.assertIsNone(load_license_info(Path(self.tmp)))


if __name__ == "__main__":
    unittest.main()
