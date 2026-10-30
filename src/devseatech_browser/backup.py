"""AF-02 Automatic Local Profile Backup.

Creates encrypted, integrity-checked snapshots of a browser profile's
persistent data, writes them atomically, prunes old snapshots by a retention
policy, and restores them with verification.

Design notes:
- Encryption uses the `cryptography` package (Fernet / AES-128-CBC + HMAC).
  It is imported lazily inside the cipher helpers so that the pure logic
  (manifest building, retention pruning, file selection, atomic writes) is
  importable and testable with only the standard library.
- Volatile caches are excluded by default to keep snapshots meaningful.
- No passphrase, key, or secret value is ever logged or placed in a manifest.
- Writes are atomic (temp file + fsync + os.replace) so an interrupted backup
  never leaves a half-written snapshot in place.

This module does not schedule itself; a caller (or the app's scheduler) decides
when to invoke `create_backup`. It also never guarantees that website
authentication inside a restored profile remains valid.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

BACKUP_SUFFIX = ".dstbak"
MANIFEST_NAME = "manifest.json"
PAYLOAD_NAME = "payload.tar"
# Directories inside a profile that are safe to skip in a snapshot.
DEFAULT_EXCLUDED_DIRS = ("cache",)


@dataclass(frozen=True)
class BackupPolicy:
    """Retention and selection policy for profile snapshots."""

    max_backups: int = 5
    excluded_dirs: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS
    # Guard against accidentally snapshotting an enormous profile.
    max_total_bytes: int = 512 * 1024 * 1024


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def iter_profile_files(
    profile_dir: Path, excluded_dirs: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS
) -> list[Path]:
    """Return regular files to snapshot, relative to ``profile_dir``.

    Symlinks are skipped so a backup can never follow a link out of the
    profile tree. Excluded top-level directories (e.g. ``cache``) are omitted.
    """
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"Profile directory not found: {profile_dir}")
    results: list[Path] = []
    for path in sorted(profile_dir.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(profile_dir)
        if rel.parts and rel.parts[0] in excluded_dirs:
            continue
        results.append(rel)
    return results


def build_manifest(profile_dir: Path, files: list[Path]) -> dict:
    """Build an integrity manifest: per-file sha256 + size, plus totals."""
    entries = []
    total = 0
    for rel in files:
        data = (profile_dir / rel).read_bytes()
        total += len(data)
        entries.append(
            {
                "path": rel.as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
        )
    return {
        "version": 1,
        "created_at": _utc_stamp(),
        "file_count": len(entries),
        "total_bytes": total,
        "files": entries,
    }


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a urlsafe-base64 Fernet key from a passphrase (scrypt)."""
    raw = hashlib.scrypt(
        passphrase.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
    )
    return base64.urlsafe_b64encode(raw)


def _encrypt(plaintext: bytes, passphrase: str) -> bytes:
    """Encrypt bytes with a passphrase. Lazy-imports cryptography."""
    try:
        from cryptography.fernet import Fernet
    except ImportError as exc:  # pragma: no cover - exercised only without dep
        raise RuntimeError(
            "Profile backup encryption requires the 'cryptography' package."
        ) from exc
    salt = os.urandom(16)
    token = Fernet(_derive_key(passphrase, salt)).encrypt(plaintext)
    # Prepend the salt so decryption can re-derive the key.
    return salt + token


def _decrypt(blob: bytes, passphrase: str) -> bytes:
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Profile backup decryption requires the 'cryptography' package."
        ) from exc
    if len(blob) < 17:
        raise ValueError("Backup payload is too short to be valid.")
    salt, token = blob[:16], blob[16:]
    try:
        return Fernet(_derive_key(passphrase, salt)).decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Backup could not be decrypted (wrong key or tampered).") from exc


def _atomic_write(dest: Path, data: bytes) -> None:
    """Write bytes to ``dest`` atomically with fsync + os.replace."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    with tmp.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(tmp, 0o600)
    tmp.replace(dest)


def _pack_payload(profile_dir: Path, files: list[Path]) -> bytes:
    """Deterministically tar the selected files into memory."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for rel in files:
            tar.add(profile_dir / rel, arcname=rel.as_posix(), recursive=False)
    return buffer.getvalue()


def prune_backups(backup_dir: Path, max_backups: int) -> list[Path]:
    """Delete all but the newest ``max_backups`` snapshots. Returns removed paths."""
    if max_backups < 1:
        raise ValueError("max_backups must be at least 1")
    snapshots = sorted(backup_dir.glob(f"*{BACKUP_SUFFIX}"))
    removed: list[Path] = []
    while len(snapshots) > max_backups:
        oldest = snapshots.pop(0)
        oldest.unlink()
        removed.append(oldest)
    return removed


def create_backup(
    profile_dir: Path,
    backup_dir: Path,
    passphrase: str,
    policy: BackupPolicy | None = None,
) -> Path:
    """Create one encrypted snapshot of ``profile_dir`` and prune old ones."""
    policy = policy or BackupPolicy()
    files = iter_profile_files(profile_dir, policy.excluded_dirs)
    manifest = build_manifest(profile_dir, files)
    if manifest["total_bytes"] > policy.max_total_bytes:
        raise ValueError(
            f"Profile snapshot ({manifest['total_bytes']} bytes) exceeds the "
            f"configured limit ({policy.max_total_bytes} bytes)."
        )
    payload = _pack_payload(profile_dir, files)
    # Bundle manifest + payload into a single tar, then encrypt the whole thing.
    bundle = io.BytesIO()
    with tarfile.open(fileobj=bundle, mode="w") as tar:
        for name, data in (
            (MANIFEST_NAME, json.dumps(manifest, indent=2).encode("utf-8")),
            (PAYLOAD_NAME, payload),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    encrypted = _encrypt(bundle.getvalue(), passphrase)

    dest = backup_dir / f"{profile_dir.name}-{_utc_stamp()}{BACKUP_SUFFIX}"
    _atomic_write(dest, encrypted)
    prune_backups(backup_dir, policy.max_backups)
    return dest


def read_manifest(backup_path: Path, passphrase: str) -> dict:
    """Decrypt a snapshot and return its manifest without restoring files."""
    bundle = _decrypt(backup_path.read_bytes(), passphrase)
    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r") as tar:
        member = tar.extractfile(MANIFEST_NAME)
        if member is None:
            raise ValueError("Backup is missing its manifest.")
        return json.loads(member.read().decode("utf-8"))


def restore_backup(
    backup_path: Path, passphrase: str, target_dir: Path
) -> dict:
    """Restore a snapshot into ``target_dir``, verifying every file hash.

    Returns the manifest. Raises ValueError if any file fails integrity
    verification; in that case ``target_dir`` is left unchanged.
    """
    bundle = _decrypt(backup_path.read_bytes(), passphrase)
    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r") as tar:
        manifest_member = tar.extractfile(MANIFEST_NAME)
        payload_member = tar.extractfile(PAYLOAD_NAME)
        if manifest_member is None or payload_member is None:
            raise ValueError("Backup bundle is incomplete.")
        manifest = json.loads(manifest_member.read().decode("utf-8"))
        payload_bytes = payload_member.read()

    # Never trust archive manifests: reject traversal, absolute paths, and
    # platform-specific separators before any filesystem modification.
    entries = manifest["files"]
    expected: dict[str, dict] = {}
    for entry in entries:
        name = entry["path"]
        parts = name.split("/")
        if (not isinstance(name, str) or not name or name.startswith("/")
                or chr(92) in name or ":" in name
                or any(part in ("", ".", "..") for part in parts)
                or name in expected):
            raise ValueError("Unsafe or duplicate backup path")
        expected[name] = entry
    staged: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(payload_bytes), mode="r") as tar:
        for name in expected:
            member = tar.extractfile(name)
            if member is None:
                raise ValueError(f"Backup payload is missing: {name}")
            data = member.read()
            if hashlib.sha256(data).hexdigest() != expected[name]["sha256"]:
                raise ValueError(f"Integrity check failed for: {name}")
            staged[name] = data

    # Only write after every file has verified.
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, data in staged.items():
        _atomic_write(target_dir / name, data)
    return manifest
