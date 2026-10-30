"""Tests for AF-13: Security and Activity Logs."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.security_logs import (
    LogCategory, LogLevel, SecurityLogger, redact_sensitive,
)


class RedactionTests(unittest.TestCase):

    def test_redacts_password(self):
        d = redact_sensitive({"password": "secret123", "name": "alice"})
        self.assertEqual(d["password"], "***REDACTED***")
        self.assertEqual(d["name"], "alice")

    def test_redacts_nested(self):
        d = redact_sensitive({"auth": {"token": "abc", "user": "bob"}})
        self.assertEqual(d["auth"]["token"], "***REDACTED***")
        self.assertEqual(d["auth"]["user"], "bob")

    def test_case_insensitive(self):
        d = redact_sensitive({"API_KEY": "xyz"})
        self.assertEqual(d["API_KEY"], "***REDACTED***")

    def test_no_redaction_needed(self):
        d = redact_sensitive({"name": "test", "count": 5})
        self.assertEqual(d, {"name": "test", "count": 5})


class SecurityLoggerTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.logger = SecurityLogger(Path(self.tmp))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_log_and_read(self):
        self.logger.log(LogLevel.INFO, LogCategory.AUTH,
                        "login", actor="admin")
        entries = self.logger.read_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].action, "login")

    def test_redaction_on_write(self):
        self.logger.log(LogLevel.WARNING, LogCategory.SECURITY,
                        "key_change", details={"old_password": "abc"})
        entries = self.logger.read_logs()
        self.assertEqual(entries[0].details["old_password"], "***REDACTED***")

    def test_filter_by_category(self):
        self.logger.log(LogLevel.INFO, LogCategory.AUTH, "login")
        self.logger.log(LogLevel.INFO, LogCategory.PROFILE, "create")
        auth = self.logger.read_logs(category=LogCategory.AUTH)
        self.assertEqual(len(auth), 1)

    def test_filter_by_level(self):
        self.logger.log(LogLevel.INFO, LogCategory.AUTH, "login")
        self.logger.log(LogLevel.ERROR, LogCategory.AUTH, "fail")
        errors = self.logger.read_logs(level=LogLevel.ERROR)
        self.assertEqual(len(errors), 1)

    def test_count(self):
        self.assertEqual(self.logger.count(), 0)
        self.logger.log(LogLevel.INFO, LogCategory.AUTH, "a")
        self.logger.log(LogLevel.INFO, LogCategory.AUTH, "b")
        self.assertEqual(self.logger.count(), 2)

    def test_limit(self):
        for i in range(10):
            self.logger.log(LogLevel.INFO, LogCategory.AUTH, f"action_{i}")
        entries = self.logger.read_logs(limit=3)
        self.assertEqual(len(entries), 3)

    def test_empty_read(self):
        self.assertEqual(self.logger.read_logs(), [])

    def test_rotation(self):
        small = SecurityLogger(Path(self.tmp), max_bytes=100)
        for i in range(20):
            small.log(LogLevel.INFO, LogCategory.AUTH, f"action_{i}")
        # Should have rotated — old file renamed
        log_dir = Path(self.tmp) / "logs"
        jsonl_files = list(log_dir.glob("*.jsonl"))
        self.assertGreater(len(jsonl_files), 1)


if __name__ == "__main__":
    unittest.main()
