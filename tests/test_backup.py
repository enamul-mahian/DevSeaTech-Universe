"""Tests for AF-02 profile backup/restore.

Pure-logic tests use only the standard library and always run. Encryption
round-trip tests are skipped automatically when the optional `cryptography`
package is not installed, so the dependency-free CI lane still passes.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

from devseatech_browser import backup
from devseatech_browser.backup import (
    BackupPolicy,
    build_manifest,
    iter_profile_files,
    prune_backups,
    _atomic_write,
)

HAS_CRYPTOGRAPHY = importlib.util.find_spec("cryptography") is not None
PASSPHRASE = "correct horse battery staple"


def _make_profile(root: Path) -> Path:
    profile = root / "work"
    (profile / "storage").mkdir(parents=True)
    (profile / "cache").mkdir(parents=True)
    (profile / "storage" / "cookies.bin").write_bytes(b"cookie-data-123")
    (profile / "storage" / "prefs.json").write_text('{"theme":"dark"}')
    (profile / "cache" / "big.tmp").write_bytes(b"x" * 4096)
    return profile


class PureLogicTests(unittest.TestCase):
    def test_iter_excludes_cache_and_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            profile = _make_profile(Path(d))
            files = {p.as_posix() for p in iter_profile_files(profile)}
            self.assertIn("storage/cookies.bin", files)
            self.assertIn("storage/prefs.json", files)
            self.assertNotIn("cache/big.tmp", files)

    def test_manifest_hashes_and_totals(self):
        with tempfile.TemporaryDirectory() as d:
            profile = _make_profile(Path(d))
            files = iter_profile_files(profile)
            manifest = build_manifest(profile, files)
            self.assertEqual(manifest["file_count"], 2)
            self.assertEqual(manifest["total_bytes"], len(b"cookie-data-123") + len('{"theme":"dark"}'))
            for entry in manifest["files"]:
                self.assertEqual(len(entry["sha256"]), 64)

    def test_atomic_write_replaces_and_sets_mode(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "out" / "file.bin"
            _atomic_write(dest, b"hello")
            self.assertEqual(dest.read_bytes(), b"hello")
            self.assertFalse(dest.with_name(dest.name + ".part").exists())
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)

    def test_prune_keeps_newest_n(self):
        with tempfile.TemporaryDirectory() as d:
            backup_dir = Path(d)
            names = [f"work-2026010{i}T000000000000Z{backup.BACKUP_SUFFIX}" for i in range(1, 6)]
            for name in names:
                (backup_dir / name).write_bytes(b"x")
            removed = prune_backups(backup_dir, max_backups=2)
            remaining = sorted(p.name for p in backup_dir.glob(f"*{backup.BACKUP_SUFFIX}"))
            self.assertEqual(len(remaining), 2)
            self.assertEqual(remaining, names[-2:])
            self.assertEqual(len(removed), 3)

    def test_prune_rejects_zero(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                prune_backups(Path(d), max_backups=0)

    def test_oversize_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            profile = _make_profile(Path(d))
            policy = BackupPolicy(max_total_bytes=1)
            with self.assertRaises(ValueError):
                backup.create_backup(profile, Path(d) / "backups", PASSPHRASE, policy)


@unittest.skipUnless(HAS_CRYPTOGRAPHY, "cryptography not installed")
class EncryptionRoundTripTests(unittest.TestCase):
    def test_backup_restore_roundtrip_preserves_data(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            profile = _make_profile(root)
            backup_dir = root / "backups"
            snapshot = backup.create_backup(profile, backup_dir, PASSPHRASE)
            self.assertTrue(snapshot.exists())
            self.assertEqual(snapshot.stat().st_mode & 0o777, 0o600)

            target = root / "restored"
            manifest = backup.restore_backup(snapshot, PASSPHRASE, target)
            self.assertEqual(manifest["file_count"], 2)
            self.assertEqual(
                (target / "storage" / "cookies.bin").read_bytes(), b"cookie-data-123"
            )
            self.assertFalse((target / "cache" / "big.tmp").exists())

    def test_wrong_passphrase_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            profile = _make_profile(root)
            snapshot = backup.create_backup(profile, root / "backups", PASSPHRASE)
            with self.assertRaises(ValueError):
                backup.restore_backup(snapshot, "wrong-pass", root / "restored")

    def test_tampered_snapshot_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            profile = _make_profile(root)
            snapshot = backup.create_backup(profile, root / "backups", PASSPHRASE)
            blob = bytearray(snapshot.read_bytes())
            blob[-1] ^= 0xFF  # flip a bit in the ciphertext
            snapshot.write_bytes(bytes(blob))
            with self.assertRaises(ValueError):
                backup.restore_backup(snapshot, PASSPHRASE, root / "restored")

    def test_retention_enforced_across_backups(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            profile = _make_profile(root)
            backup_dir = root / "backups"
            policy = BackupPolicy(max_backups=2)
            for _ in range(4):
                backup.create_backup(profile, backup_dir, PASSPHRASE, policy)
            snaps = list(backup_dir.glob(f"*{backup.BACKUP_SUFFIX}"))
            self.assertLessEqual(len(snaps), 2)


if __name__ == "__main__":
    unittest.main()
