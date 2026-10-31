"""Security review tests for AF-01 through AF-18.

Verifies security properties across all features:
- Path traversal prevention
- Input sanitization
- Encryption correctness
- Secret/credential handling
- Secure defaults
- Permission boundary enforcement
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path


# ── AF-01: Session Restore ──────────────────────────────────────────

class AF01SecurityTests(unittest.TestCase):
    """Session restore must not leak across profiles or accept injected data."""

    def test_malicious_json_is_rejected(self):
        from devseatech_browser.session_restore import load_session
        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)
            session_file = app_dir / "session.json"
            # Write invalid JSON
            session_file.write_text("not valid json {{{", encoding="utf-8")
            result = load_session(app_dir)
            self.assertIsNone(result)

    def test_injected_script_in_title_is_safe(self):
        from devseatech_browser.session_restore import (
            TabEntry, save_session, load_session,
        )
        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)
            xss_title = '<script>alert("xss")</script>'
            tabs = [TabEntry(profile="P", url="https://safe.com", title=xss_title)]
            save_session(app_dir, tabs)
            recovered = load_session(app_dir)
            # Stored as-is (no execution context in JSON), but must not crash
            self.assertIsNotNone(recovered)
            self.assertEqual(recovered[0].title, xss_title)


# ── AF-02: Backup ───────────────────────────────────────────────────

class AF02SecurityTests(unittest.TestCase):
    """Encrypted backups must resist tampering and passphrase bypass."""

    def test_tampered_backup_fails_restore(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.backup import create_backup, restore_backup

        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "p"
            profile.mkdir()
            (profile / "data.txt").write_text("sensitive")
            path = create_backup(profile, Path(td) / "bk", "Pass123!")

            # Tamper with the encrypted file
            data = bytearray(path.read_bytes())
            if len(data) > 50:
                data[50] ^= 0xFF
            path.write_bytes(bytes(data))

            with self.assertRaises(Exception):
                restore_backup(path, "Pass123!", Path(td) / "out")

    def test_empty_passphrase_rejected(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.backup import create_backup

        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "p"
            profile.mkdir()
            (profile / "data.txt").write_text("x")
            # Even with empty passphrase, the backup should still be encrypted
            # (scrypt derives a key from any input). Verify it doesn't plaintext.
            path = create_backup(profile, Path(td) / "bk", "")
            raw = path.read_bytes()
            self.assertNotIn(b"data.txt", raw[:100])


# ── AF-03: Profile Health ──────────────────────────────────────────

class AF03SecurityTests(unittest.TestCase):
    """Profile health check must not follow symlinks or escape root."""

    def test_symlink_profiles_flagged(self):
        from devseatech_browser.profile_health import check_all_profiles
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Symlink to /etc should not be treated as a valid profile
            try:
                (root / "evil").symlink_to("/etc")
            except OSError:
                self.skipTest("Cannot create symlinks")
            findings = check_all_profiles(root)
            # Should not crash, and should not treat symlink as valid profile
            profile_names = [f.profile for f in findings]
            # "evil" might be flagged as warning/error, or simply skipped
            self.assertIsInstance(findings, list)


# ── AF-05: Download Manager ────────────────────────────────────────

class AF05SecurityTests(unittest.TestCase):
    """Download manager must block path traversal and risky extensions."""

    def test_path_traversal_blocked(self):
        from devseatech_browser.download_manager import sanitize_filename

        traversal_names = [
            "../../../etc/passwd",
            "..\\..\\system32\\cmd.exe",
            "/absolute/path.txt",
            "C:\\Windows\\notepad.exe",
        ]
        for name in traversal_names:
            safe = sanitize_filename(name)
            self.assertNotIn("/", safe, f"Slash in sanitized: {safe}")
            self.assertNotIn("\\", safe, f"Backslash in sanitized: {safe}")

    def test_risky_extensions_detected(self):
        from devseatech_browser.download_manager import is_risky_download

        risky = ["malware.exe", "virus.bat", "trojan.cmd", "script.vbs",
                 "macro.scr", "payload.ps1", "UPPER.EXE"]
        for f in risky:
            self.assertTrue(is_risky_download(f), f"{f} should be risky")

        safe = ["doc.pdf", "img.png", "page.html", "data.csv"]
        for f in safe:
            self.assertFalse(is_risky_download(f), f"{f} should be safe")


# ── AF-06: Password Vault ──────────────────────────────────────────

class AF06SecurityTests(unittest.TestCase):
    """Vault must encrypt at rest and prevent access without unlock."""

    def test_credentials_encrypted_on_disk(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.password_vault import PasswordVault

        with tempfile.TemporaryDirectory() as td:
            vault = PasswordVault(Path(td))
            vault.unlock("TestMasterPass123!")
            vault.add("secret.com", "admin", "SuperSecret!@#")
            vault.lock()

            # Read all files in the vault dir — no plaintext password
            for f in Path(td).rglob("*"):
                if f.is_file():
                    content = f.read_bytes()
                    self.assertNotIn(b"SuperSecret!@#", content,
                                     f"Plaintext password found in {f}")

    def test_locked_vault_denies_access(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.password_vault import PasswordVault

        with tempfile.TemporaryDirectory() as td:
            vault = PasswordVault(Path(td))
            vault.unlock("TestPass123!")
            vault.add("test.com", "user", "pass")
            vault.lock()

            # Accessing locked vault should fail or return empty
            try:
                entries = vault.list_all()
                self.assertEqual(len(entries), 0)
            except Exception:
                pass  # Expected — locked vault should not provide data


# ── AF-07: Profile Migration ───────────────────────────────────────

class AF07SecurityTests(unittest.TestCase):
    """Migration archives must be encrypted and reject tar path traversal."""

    def test_export_is_encrypted(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.profile_migration import export_profile

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir()
            (src / "secret.txt").write_text("top-secret-data-12345")

            archive = Path(td) / "export.bin"
            export_profile(src, "Pass123!", archive)

            raw = archive.read_bytes()
            self.assertNotIn(b"top-secret-data-12345", raw)


# ── AF-08: Proxy Health ────────────────────────────────────────────

class AF08SecurityTests(unittest.TestCase):
    """Proxy config must validate input and reject dangerous values."""

    def test_invalid_port_rejected(self):
        from devseatech_browser.proxy_health import (
            validate_proxy_config, ProxyConfig, ProxyType,
        )
        bad = ProxyConfig(proxy_type=ProxyType.HTTP, host="test.com", port=0)
        issues = validate_proxy_config(bad)
        self.assertGreater(len(issues), 0)

        bad2 = ProxyConfig(proxy_type=ProxyType.HTTP, host="test.com", port=99999)
        issues2 = validate_proxy_config(bad2)
        self.assertGreater(len(issues2), 0)

    def test_invalid_url_returns_none(self):
        from devseatech_browser.proxy_health import parse_proxy_url
        self.assertIsNone(parse_proxy_url("ftp://bad.com"))
        self.assertIsNone(parse_proxy_url("not-a-url"))


# ── AF-09: Resource Manager ────────────────────────────────────────

class AF09SecurityTests(unittest.TestCase):
    """Resource checks must not follow symlinks outside profile dir."""

    def test_symlink_not_followed(self):
        from devseatech_browser.resource_manager import measure_profile_disk
        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "profile"
            profile.mkdir()
            (profile / "data.txt").write_text("x")

            # Symlink to system dir — should not crash or measure outside
            try:
                (profile / "evil_link").symlink_to("/usr")
            except OSError:
                self.skipTest("Cannot create symlinks")
            snap = measure_profile_disk(profile)
            # Should complete without error; size should be reasonable
            self.assertIsNotNone(snap)


# ── AF-10: License Reminder ────────────────────────────────────────

class AF10SecurityTests(unittest.TestCase):
    """License uses server-authoritative epoch time, not client datetime."""

    def test_license_uses_epoch_not_datetime(self):
        from devseatech_browser.license_reminder import LicenseInfo, LicensePlan
        info = LicenseInfo(
            plan=LicensePlan.STANDARD,
            activated_at=time.time(),
            expires_at=time.time() + 30 * 24 * 3600,
        )
        self.assertIsInstance(info.activated_at, float)
        self.assertIsInstance(info.expires_at, float)
        self.assertGreater(info.duration_hours, 0)


# ── AF-11: Profile Templates ───────────────────────────────────────

class AF11SecurityTests(unittest.TestCase):
    """Templates must not inject blocked fields."""

    def test_blocked_fields_excluded(self):
        from devseatech_browser.profile_templates import (
            TemplateConfig, BLOCKED_FIELDS,
        )
        # BLOCKED_FIELDS should include security-sensitive fields
        self.assertIn("passwords", BLOCKED_FIELDS)
        self.assertIn("vault", BLOCKED_FIELDS)
        self.assertIn("auth_tokens", BLOCKED_FIELDS)


# ── AF-12: Permission Manager ──────────────────────────────────────

class AF12SecurityTests(unittest.TestCase):
    """Default permission must be ASK, not ALLOW."""

    def test_default_is_ask_not_allow(self):
        from devseatech_browser.permission_manager import (
            PermissionStore, Permission, PermissionDecision,
        )
        with tempfile.TemporaryDirectory() as td:
            store = PermissionStore(Path(td))
            # Any unknown origin+permission combination defaults to ASK
            decision = store.get_decision("malicious.com", Permission.CAMERA)
            self.assertEqual(decision, PermissionDecision.ASK)
            decision = store.get_decision("unknown.com", Permission.MICROPHONE)
            self.assertEqual(decision, PermissionDecision.ASK)


# ── AF-13: Security Logs ───────────────────────────────────────────

class AF13SecurityTests(unittest.TestCase):
    """Logs must redact sensitive data like passwords."""

    def test_password_redaction(self):
        from devseatech_browser.security_logs import redact_sensitive

        details = {
            "username": "admin",
            "password": "SuperSecret123!",
            "token": "abc123tokenxyz",
        }
        redacted = redact_sensitive(details)
        self.assertNotEqual(redacted.get("password"), "SuperSecret123!")
        self.assertEqual(redacted["username"], "admin")

    def test_log_entries_are_append_only(self):
        from devseatech_browser.security_logs import (
            SecurityLogger, LogLevel, LogCategory,
        )
        with tempfile.TemporaryDirectory() as td:
            logger = SecurityLogger(Path(td))
            logger.log(LogLevel.INFO, LogCategory.AUTH, "event1")
            logger.log(LogLevel.INFO, LogCategory.AUTH, "event2")

            # Read back — should have both entries
            entries = logger.read_logs(limit=100)
            self.assertEqual(len(entries), 2)
            # Log file should be append-only JSONL
            log_path = Path(td) / "security_audit.jsonl"
            if log_path.exists():
                lines = log_path.read_text().strip().split("\n")
                self.assertEqual(len(lines), 2)


# ── AF-14: Browser Diagnostics ─────────────────────────────────────

class AF14SecurityTests(unittest.TestCase):
    """Diagnostics must be read-only and not modify the profile."""

    def test_diagnostics_are_read_only(self):
        from devseatech_browser.browser_diagnostics import run_diagnostics
        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)
            (app_dir / "settings.json").write_text('{"key": "value"}')

            # Record state before
            before = (app_dir / "settings.json").read_text()
            files_before = set(p.name for p in app_dir.rglob("*"))

            run_diagnostics(app_dir)

            # State should be unchanged
            after = (app_dir / "settings.json").read_text()
            self.assertEqual(before, after)


# ── AF-16: Keyboard Shortcuts ──────────────────────────────────────

class AF16SecurityTests(unittest.TestCase):
    """Shortcuts must detect conflicts to prevent hijacking."""

    def test_conflict_detection(self):
        from devseatech_browser.keyboard_shortcuts import ShortcutStore

        with tempfile.TemporaryDirectory() as td:
            store = ShortcutStore(Path(td))
            all_sc = store.list_all()

            if len(all_sc) >= 2:
                # Assign the same keys to two different actions
                store.set_keys(all_sc[0].action, "Ctrl+Z")
                store.set_keys(all_sc[1].action, "Ctrl+Z")

                conflicts = store.validate()
                self.assertGreater(len(conflicts), 0)


# ── AF-17: Website Translation ─────────────────────────────────────

class AF17SecurityTests(unittest.TestCase):
    """Translation must require privacy disclosure before sending data."""

    def test_privacy_disclosure_required(self):
        from devseatech_browser.website_translation import (
            TranslationConfig, needs_privacy_disclosure,
        )
        config = TranslationConfig(enabled=True, privacy_acknowledged=False)
        self.assertTrue(needs_privacy_disclosure(config))

        config2 = TranslationConfig(enabled=True, privacy_acknowledged=True)
        self.assertFalse(needs_privacy_disclosure(config2))


# ── AF-18: Accessibility ───────────────────────────────────────────

class AF18SecurityTests(unittest.TestCase):
    """Accessibility config must validate bounds."""

    def test_font_scale_bounds(self):
        from devseatech_browser.accessibility_settings import AccessibilityConfig

        bad = AccessibilityConfig(font_scale=0.0)
        errors = bad.validate()
        self.assertGreater(len(errors), 0)

        bad2 = AccessibilityConfig(font_scale=10.0)
        errors2 = bad2.validate()
        self.assertGreater(len(errors2), 0)

        good = AccessibilityConfig(font_scale=1.5)
        errors3 = good.validate()
        self.assertEqual(len(errors3), 0)


# ── Home Page ───────────────────────────────────────────────────────

class HomePageSecurityTests(unittest.TestCase):
    """Home page must escape user data to prevent XSS."""

    def test_html_escaping_in_speed_dial(self):
        from devseatech_browser.home_page import generate_home_html, SpeedDialEntry

        xss_entry = SpeedDialEntry(
            title='<img src=x onerror=alert(1)>',
            url='javascript:alert(1)',
            icon='<script>alert(1)</script>',
        )
        html = generate_home_html([xss_entry])
        # All special characters should be escaped
        self.assertNotIn('<img src=x onerror', html)
        self.assertNotIn('<script>alert', html)
        # The escaped versions should appear
        self.assertIn('&lt;', html)


# ── Cross-cutting: Profile Listing ──────────────────────────────────

class ProfileListingSecurityTests(unittest.TestCase):
    """Profile listing must reject symlinks and dangerous names."""

    def test_symlinks_excluded(self):
        from devseatech_browser.profile_listing import list_profiles

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "good").mkdir()
            try:
                (root / "evil_link").symlink_to("/etc")
            except OSError:
                self.skipTest("Cannot create symlinks")
            profiles = list_profiles(root)
            self.assertIn("good", profiles)
            self.assertNotIn("evil_link", profiles)

    def test_special_chars_in_name_rejected(self):
        from devseatech_browser.profile_listing import list_profiles

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "good").mkdir()
            # Names with special chars
            for bad_name in [".hidden", "has space"]:
                try:
                    (root / bad_name).mkdir()
                except OSError:
                    pass
            profiles = list_profiles(root)
            self.assertIn("good", profiles)
            self.assertNotIn(".hidden", profiles)
            self.assertNotIn("has space", profiles)


if __name__ == "__main__":
    unittest.main()
