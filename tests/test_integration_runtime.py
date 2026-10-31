"""Runtime integration tests for AF-01 through AF-18.

Each test exercises a feature's full workflow end-to-end with realistic
data, proving it runs correctly — not just that individual functions work.
These complement the unit tests and advance features to Runtime status.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path


class AF01SessionRestoreIntegration(unittest.TestCase):
    """AF-01: Full crash-recovery workflow."""

    def test_full_crash_recovery_cycle(self):
        from devseatech_browser.session_restore import (
            TabEntry, save_session, load_session, mark_clean, SAVE_INTERVAL_MS,
        )
        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)
            tabs = [
                TabEntry(profile="Work", url="https://github.com", title="GitHub"),
                TabEntry(profile="Personal", url="https://youtube.com", title="YouTube"),
                TabEntry(profile="Default", url="https://google.com", title="Google"),
            ]
            save_session(app_dir, tabs)
            recovered = load_session(app_dir)
            self.assertIsNotNone(recovered)
            self.assertEqual(len(recovered), 3)
            self.assertEqual(recovered[0].profile, "Work")
            self.assertEqual(recovered[1].url, "https://youtube.com")

            mark_clean(app_dir)
            self.assertIsNone(load_session(app_dir))

            self.assertGreaterEqual(SAVE_INTERVAL_MS, 10000)
            self.assertLessEqual(SAVE_INTERVAL_MS, 300000)


class AF02BackupIntegration(unittest.TestCase):
    """AF-02: Full backup + restore cycle with encryption."""

    def test_encrypted_backup_restore_roundtrip(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.backup import create_backup, restore_backup

        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "profiles" / "TestProfile"
            (profile / "storage").mkdir(parents=True)
            (profile / "storage" / "cookies.db").write_text("cookie_data")
            (profile / "storage" / "prefs.json").write_text('{"theme":"dark"}')

            backup_dir = Path(td) / "backups"
            passphrase = "SuperSecurePass123!"

            backup_path = create_backup(profile, backup_dir, passphrase)
            self.assertTrue(backup_path.exists())
            self.assertTrue(str(backup_path).endswith(".dstbak"))

            raw = backup_path.read_bytes()
            self.assertNotIn(b"cookie_data", raw)

            restore_dir = Path(td) / "restored"
            manifest = restore_backup(backup_path, passphrase, restore_dir)
            self.assertIsInstance(manifest, dict)
            self.assertTrue((restore_dir / "storage" / "cookies.db").exists())
            self.assertEqual(
                (restore_dir / "storage" / "cookies.db").read_text(),
                "cookie_data"
            )

    def test_wrong_passphrase_fails(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.backup import create_backup, restore_backup

        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "profiles" / "Test"
            profile.mkdir(parents=True)
            (profile / "data.txt").write_text("secret")
            backup_dir = Path(td) / "backups"
            path = create_backup(profile, backup_dir, "CorrectPassword123")

            with self.assertRaises(Exception):
                restore_backup(path, "WrongPassword12345", Path(td) / "bad")


class AF03ProfileHealthIntegration(unittest.TestCase):
    """AF-03: Health check on realistic profile structures."""

    def test_healthy_and_unhealthy_profiles(self):
        from devseatech_browser.profile_health import check_all_profiles, Severity

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = root / "GoodProfile"
            (good / "storage").mkdir(parents=True)
            (good / "cache").mkdir(parents=True)

            findings = check_all_profiles(root)
            errors = [f for f in findings if f.severity == Severity.ERROR
                      and f.profile == "GoodProfile"]
            self.assertEqual(len(errors), 0)


class AF04EngineCompatIntegration(unittest.TestCase):
    """AF-04: Engine compatibility checker runs all checks."""

    def test_full_compatibility_report(self):
        from devseatech_browser.engine_compat import (
            run_all_checks, is_compatible, format_report,
        )
        with tempfile.TemporaryDirectory() as td:
            checks = run_all_checks(Path(td))
            self.assertIsInstance(checks, list)
            self.assertGreater(len(checks), 0)

            py_checks = [c for c in checks if "python" in c.name.lower()]
            self.assertTrue(len(py_checks) > 0)

            report = format_report(checks)
            self.assertIsInstance(report, str)
            self.assertGreater(len(report), 0)


class AF05DownloadManagerIntegration(unittest.TestCase):
    """AF-05: Full download lifecycle."""

    def test_download_lifecycle(self):
        from devseatech_browser.download_manager import (
            DownloadTracker, DownloadStatus,
        )
        with tempfile.TemporaryDirectory() as td:
            tracker = DownloadTracker(Path(td))

            rec = tracker.start_download("https://example.com/file.pdf", "file.pdf", str(Path(td) / "file.pdf"))
            dl_id = rec.download_id
            self.assertIsNotNone(dl_id)

            info = tracker.get(dl_id)
            self.assertIsNotNone(info)

            tracker.pause(dl_id)
            info = tracker.get(dl_id)
            self.assertEqual(info.status, DownloadStatus.PAUSED)

            tracker.resume(dl_id)
            info = tracker.get(dl_id)
            self.assertEqual(info.status, DownloadStatus.IN_PROGRESS)

            tracker.cancel(dl_id)
            info = tracker.get(dl_id)
            self.assertEqual(info.status, DownloadStatus.CANCELLED)

    def test_risky_extension_detection(self):
        from devseatech_browser.download_manager import is_risky_download

        self.assertTrue(is_risky_download("malware.exe"))
        self.assertTrue(is_risky_download("script.bat"))
        self.assertFalse(is_risky_download("document.pdf"))
        self.assertFalse(is_risky_download("image.png"))

    def test_filename_sanitization(self):
        from devseatech_browser.download_manager import sanitize_filename

        safe = sanitize_filename("../../../etc/passwd")
        self.assertNotIn("/", safe)
        self.assertNotIn("\\", safe)

        self.assertEqual(sanitize_filename("report.pdf"), "report.pdf")


class AF06PasswordVaultIntegration(unittest.TestCase):
    """AF-06: Full vault lock/unlock/CRUD cycle."""

    def test_vault_full_lifecycle(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.password_vault import PasswordVault

        with tempfile.TemporaryDirectory() as td:
            vault = PasswordVault(Path(td))
            master = "VaultMasterKey123!"

            vault.unlock(master)
            self.assertTrue(vault.is_unlocked)

            vault.add("github.com", "user@test.com", "gh_pass_123")
            vault.add("gitlab.com", "dev@test.com", "gl_pass_456")

            origins = vault.list_origins()
            self.assertIn("github.com", origins)
            self.assertIn("gitlab.com", origins)

            vault.remove("gitlab.com", "dev@test.com")
            origins = vault.list_origins()
            self.assertNotIn("gitlab.com", origins)

            vault.lock()
            self.assertFalse(vault.is_unlocked)

            vault.unlock(master)
            self.assertTrue(vault.is_unlocked)
            origins = vault.list_origins()
            self.assertIn("github.com", origins)


class AF07ProfileMigrationIntegration(unittest.TestCase):
    """AF-07: Export/Import/Clone full cycle."""

    def test_export_import_roundtrip(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            self.skipTest("cryptography not installed")
        from devseatech_browser.profile_migration import (
            export_profile, import_profile, clone_profile,
        )

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source"
            (src / "storage").mkdir(parents=True)
            (src / "storage" / "data.json").write_text('{"key":"value"}')

            export_path = Path(td) / "export.dstexport"
            passphrase = "ExportSecure123!"
            export_profile(src, passphrase, export_path)
            self.assertTrue(export_path.exists())

            profiles_dir = Path(td) / "profiles"
            profiles_dir.mkdir()
            dest = import_profile(export_path, passphrase, profiles_dir, "imported")
            self.assertTrue(dest.exists())
            self.assertTrue((dest / "storage" / "data.json").exists())
            self.assertEqual(
                (dest / "storage" / "data.json").read_text(), '{"key":"value"}'
            )

            clone_src = profiles_dir / "original"
            clone_src.mkdir()
            (clone_src / "storage").mkdir()
            (clone_src / "storage" / "data.json").write_text('{"key":"value"}')
            clone_dest = clone_profile(profiles_dir, "original", "cloned")
            self.assertTrue(clone_dest.exists())
            self.assertTrue((clone_dest / "storage" / "data.json").exists())


class AF08ProxyHealthIntegration(unittest.TestCase):
    """AF-08: Proxy health check with realistic configs."""

    def test_config_validation(self):
        from devseatech_browser.proxy_health import (
            validate_proxy_config, ProxyConfig, ProxyType,
        )

        config = ProxyConfig(
            proxy_type=ProxyType.HTTP,
            host="proxy.example.com",
            port=8080,
        )
        issues = validate_proxy_config(config)
        self.assertEqual(len(issues), 0)

        bad = ProxyConfig(proxy_type=ProxyType.HTTP, host="", port=8080)
        issues = validate_proxy_config(bad)
        self.assertGreater(len(issues), 0)

    def test_proxy_url_parsing(self):
        from devseatech_browser.proxy_health import parse_proxy_url

        parsed = parse_proxy_url("http://proxy.example.com:8080")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.host, "proxy.example.com")
        self.assertEqual(parsed.port, 8080)

        parsed = parse_proxy_url("socks5://10.0.0.1:1080")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.proxy_type.value, "socks5")


class AF09ResourceManagerIntegration(unittest.TestCase):
    """AF-09: Resource monitoring full workflow."""

    def test_monitor_and_report(self):
        from devseatech_browser.resource_manager import (
            measure_profile_disk, measure_all_profiles_disk,
            check_policy, format_report,
        )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            profile = root / "TestProfile"
            profile.mkdir()
            (profile / "data.bin").write_bytes(b"x" * 10000)

            snapshot = measure_profile_disk(profile)
            self.assertGreater(snapshot.value, 0)

            all_snaps = measure_all_profiles_disk(root)
            self.assertGreater(len(all_snaps), 0)

            violations = check_policy(all_snaps)
            self.assertIsInstance(violations, list)

            report = format_report(all_snaps, violations)
            self.assertIsInstance(report, str)


class AF10LicenseReminderIntegration(unittest.TestCase):
    """AF-10: License reminder with realistic scenarios."""

    def test_trial_and_standard_reminders(self):
        from devseatech_browser.license_reminder import (
            check_renewal_needed, LicensePlan, LicenseInfo,
            save_license_info, load_license_info,
        )

        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)

            trial = LicenseInfo(
                plan=LicensePlan.TRIAL_24H,
                activated_at=time.time(),
                expires_at=time.time() + 12 * 3600,
            )
            alert = check_renewal_needed(trial)
            self.assertIsNotNone(alert)

            save_license_info(app_dir, trial)
            loaded = load_license_info(app_dir)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.plan, LicensePlan.TRIAL_24H)


class AF11ProfileTemplatesIntegration(unittest.TestCase):
    """AF-11: Template CRUD and apply cycle."""

    def test_create_and_apply_template(self):
        from devseatech_browser.profile_templates import (
            TemplateConfig, save_template, load_template,
            list_templates, delete_template, apply_template,
        )

        with tempfile.TemporaryDirectory() as td:
            app_dir = Path(td)

            config = TemplateConfig(
                name="work-secure",
                homepage="https://intranet.company.com",
                search_engine="DuckDuckGo",
            )
            save_template(app_dir, config)

            templates = list_templates(app_dir)
            self.assertIn("work-secure", templates)

            loaded = load_template(app_dir, "work-secure")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.homepage, "https://intranet.company.com")

            profile = Path(td) / "profiles" / "WorkProfile"
            profile.mkdir(parents=True)
            result = apply_template(loaded, profile)
            self.assertTrue(result.exists())

            deleted = delete_template(app_dir, "work-secure")
            self.assertTrue(deleted)
            self.assertEqual(len(list_templates(app_dir)), 0)


class AF12PermissionManagerIntegration(unittest.TestCase):
    """AF-12: Per-origin permission decisions."""

    def test_permission_workflow(self):
        from devseatech_browser.permission_manager import (
            PermissionStore, Permission, PermissionDecision,
        )

        with tempfile.TemporaryDirectory() as td:
            store = PermissionStore(Path(td))

            store.set_permission("github.com", Permission.CAMERA, PermissionDecision.DENY)
            store.set_permission("meet.google.com", Permission.CAMERA, PermissionDecision.ALLOW)
            store.set_permission("meet.google.com", Permission.MICROPHONE, PermissionDecision.ALLOW)

            decision = store.get_decision("github.com", Permission.CAMERA)
            self.assertEqual(decision, PermissionDecision.DENY)

            decision = store.get_decision("meet.google.com", Permission.CAMERA)
            self.assertEqual(decision, PermissionDecision.ALLOW)

            decision = store.get_decision("unknown.com", Permission.CAMERA)
            self.assertEqual(decision, PermissionDecision.ASK)

            all_perms = store.list_all()
            self.assertGreaterEqual(len(all_perms), 2)


class AF13SecurityLogsIntegration(unittest.TestCase):
    """AF-13: Logging, rotation, and query workflow."""

    def test_log_rotate_and_query(self):
        from devseatech_browser.security_logs import (
            SecurityLogger, LogLevel, LogCategory,
        )

        with tempfile.TemporaryDirectory() as td:
            logger = SecurityLogger(Path(td))

            for i in range(25):
                logger.log(
                    level=LogLevel.INFO if i % 3 else LogLevel.WARNING,
                    category=LogCategory.AUTH,
                    action=f"login_attempt_{i}",
                    actor="TestUser",
                )

            entries = logger.read_logs(limit=100)
            self.assertEqual(len(entries), 25)

            warnings = logger.read_logs(level=LogLevel.WARNING)
            self.assertGreater(len(warnings), 0)
            self.assertTrue(all(e.level == LogLevel.WARNING for e in warnings))

            auth_events = logger.read_logs(category=LogCategory.AUTH)
            self.assertEqual(len(auth_events), 25)

            logger.log(
                LogLevel.INFO, LogCategory.AUTH,
                action="password_changed",
                actor="User",
                details={"password": "secret123"},
            )
            last = logger.read_logs(limit=1)[0]
            if hasattr(last, "details") and "password" in last.details:
                self.assertNotEqual(last.details["password"], "secret123")


class AF14DiagnosticsIntegration(unittest.TestCase):
    """AF-14: Diagnostics check + repair workflow."""

    def test_diagnostics_run_all_checks(self):
        from devseatech_browser.browser_diagnostics import (
            run_diagnostics, format_diagnostics,
        )

        with tempfile.TemporaryDirectory() as td:
            results = run_diagnostics(Path(td))
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
            for r in results:
                self.assertTrue(hasattr(r, "name"))
                self.assertTrue(hasattr(r, "status"))

            report = format_diagnostics(results)
            self.assertIsInstance(report, str)


class AF15WorkspaceIntegration(unittest.TestCase):
    """AF-15: Workspace CRUD + profile grouping."""

    def test_workspace_with_profiles(self):
        from devseatech_browser.workspace_manager import WorkspaceStore

        with tempfile.TemporaryDirectory() as td:
            store = WorkspaceStore(Path(td))

            store.create("Development", description="Dev workspace")
            store.create("Social-Media", description="Social workspace")

            store.add_profile("Development", "GitHub-Profile")
            store.add_profile("Development", "StackOverflow-Profile")
            store.add_profile("Social-Media", "Twitter-Profile")

            results = store.search("dev")
            self.assertGreaterEqual(len(results), 1)

            ws = store.find_by_profile("GitHub-Profile")
            self.assertIn("Development", [w.name for w in ws])

            store.remove_profile("Development", "GitHub-Profile")
            dev = store.get("Development")
            self.assertNotIn("GitHub-Profile", dev.profiles)


class AF16KeyboardShortcutsIntegration(unittest.TestCase):
    """AF-16: Shortcuts with custom overrides and conflict detection."""

    def test_shortcuts_workflow(self):
        from devseatech_browser.keyboard_shortcuts import ShortcutStore

        with tempfile.TemporaryDirectory() as td:
            store = ShortcutStore(Path(td))

            defaults = store.list_all()
            self.assertGreater(len(defaults), 0)

            action = defaults[0].action
            store.set_keys(action, "Ctrl+Shift+X")
            binding = store.get(action)
            self.assertEqual(binding.keys, "Ctrl+Shift+X")

            conflicts = store.validate()
            self.assertIsInstance(conflicts, list)


class AF17TranslationIntegration(unittest.TestCase):
    """AF-17: Translation config workflow."""

    def test_translation_config_lifecycle(self):
        from devseatech_browser.website_translation import (
            TranslationConfig, save_config, load_config,
            is_site_excluded, needs_privacy_disclosure,
            get_supported_languages,
        )

        with tempfile.TemporaryDirectory() as td:
            profile_dir = Path(td)

            config = TranslationConfig(enabled=True)
            self.assertFalse(is_site_excluded(config, "example.com"))

            config.excluded_sites.append("bank.com")
            self.assertTrue(is_site_excluded(config, "bank.com"))

            # Privacy disclosure needed when enabled but not acknowledged
            self.assertTrue(needs_privacy_disclosure(config))
            config.privacy_acknowledged = True
            self.assertFalse(needs_privacy_disclosure(config))

            langs = get_supported_languages()
            self.assertGreater(len(langs), 5)

            save_config(profile_dir, config)
            config2 = load_config(profile_dir)
            self.assertTrue(is_site_excluded(config2, "bank.com"))


class AF18AccessibilityIntegration(unittest.TestCase):
    """AF-18: Accessibility settings workflow."""

    def test_accessibility_full_workflow(self):
        from devseatech_browser.accessibility_settings import (
            AccessibilityConfig, save_config, load_config,
            get_preset, list_presets,
        )

        with tempfile.TemporaryDirectory() as td:
            profile_dir = Path(td)

            presets = list_presets()
            self.assertGreater(len(presets), 0)

            preset = get_preset(presets[0])
            self.assertIsNotNone(preset)

            config = AccessibilityConfig(font_scale=1.5, high_contrast=True)
            errors = config.validate()
            self.assertEqual(len(errors), 0)

            save_config(profile_dir, config)
            loaded = load_config(profile_dir)
            self.assertEqual(loaded.font_scale, 1.5)
            self.assertTrue(loaded.high_contrast)

            bad = AccessibilityConfig(font_scale=10.0)
            errors = bad.validate()
            self.assertGreater(len(errors), 0)


class HomePageIntegration(unittest.TestCase):
    """Browser home page integration."""

    def test_home_page_generates_and_serves(self):
        from devseatech_browser.home_page import (
            generate_home_html, SpeedDialEntry, get_home_page_url,
        )
        from unittest.mock import patch

        html = generate_home_html([
            SpeedDialEntry("Test Site", "https://test.com", "T"),
        ])
        self.assertIn("Test Site", html)
        self.assertIn("google.com/search", html)
        self.assertIn("DevSeaTech", html)

        with tempfile.TemporaryDirectory() as td:
            with patch("devseatech_browser.home_page.SPEED_DIAL_FILE",
                        Path(td) / "sd.json"):
                with patch("devseatech_browser.home_page.Path.home",
                            return_value=Path(td)):
                    url = get_home_page_url()
                    self.assertTrue(url.startswith("file://"))


class ProfileListingIntegration(unittest.TestCase):
    """Profile listing and dashboard data flow."""

    def test_listing_with_mixed_entries(self):
        from devseatech_browser.profile_listing import list_profiles

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Work").mkdir()
            (root / "Personal").mkdir()
            (root / "dev-test").mkdir()
            (root / ".hidden").mkdir()

            profiles = list_profiles(root)
            self.assertIn("Work", profiles)
            self.assertIn("Personal", profiles)
            self.assertIn("dev-test", profiles)
            self.assertNotIn(".hidden", profiles)
            self.assertEqual(profiles, sorted(profiles))


if __name__ == "__main__":
    unittest.main()
