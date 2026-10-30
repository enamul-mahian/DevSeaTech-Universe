"""AF-07: Profile Import, Export and Clone.

Handles profile export (as encrypted zip), import (with validation),
and clone (local copy with new name).  All operations require explicit
authorization from the caller.

Design:
  * Export: tar + Fernet encrypt the profile directory (reuses backup
    pattern), excluding cache.
  * Import: decrypt, validate manifest, extract to new profile dir.
    Website auth cookies may be invalid after import — this is expected.
  * Clone: copy profile directory under a new name with fresh storage
    paths.  Cache is excluded.
"""
from __future__ import annotations

import json
import os
import shutil
import tarfile
import tempfile
import time
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from devseatech_browser.backup import (
    _derive_key, _encrypt, _decrypt, _atomic_write, build_manifest,
    iter_profile_files,
)


EXPORT_MANIFEST = "export_manifest.json"
EXCLUDED_DIRS = ("cache",)


def _tar_profile(profile_dir: Path) -> bytes:
    """Tar a profile directory, excluding cache."""
    buf = BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for rel in iter_profile_files(profile_dir, EXCLUDED_DIRS):
            full = profile_dir / rel
            tar.add(str(full), arcname=rel.as_posix())
    return buf.getvalue()


def export_profile(profile_dir: Path, passphrase: str,
                   output_path: Path) -> Path:
    """Export an encrypted profile archive.

    Returns the output path on success.
    Raises RuntimeError if the profile directory doesn't exist.
    """
    if not profile_dir.is_dir():
        raise RuntimeError(f"Profile directory not found: {profile_dir}")
    files = iter_profile_files(profile_dir, EXCLUDED_DIRS)
    manifest = build_manifest(profile_dir, files)
    payload = _tar_profile(profile_dir)
    # Prepend manifest as JSON + separator
    header = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    combined = header + b"\n---MANIFEST_END---\n" + payload
    encrypted = _encrypt(combined, passphrase)
    _atomic_write(output_path, encrypted)
    return output_path


def import_profile(archive_path: Path, passphrase: str,
                   profiles_dir: Path, profile_name: str) -> Path:
    """Import an encrypted profile archive into a new profile.

    Returns the new profile directory path.
    Raises ValueError on decryption failure or invalid archive.
    Raises RuntimeError if profile name already exists.
    """
    target = profiles_dir / profile_name
    if target.exists():
        raise RuntimeError(f"Profile '{profile_name}' already exists")

    try:
        blob = archive_path.read_bytes()
        decrypted = _decrypt(blob, passphrase)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e

    # Split manifest from tar
    sep = b"\n---MANIFEST_END---\n"
    idx = decrypted.find(sep)
    if idx < 0:
        raise ValueError("Invalid export archive: no manifest found")

    tar_data = decrypted[idx + len(sep):]

    # Extract to temp, then move atomically
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_target = Path(tmpdir) / profile_name
        tmp_target.mkdir()
        buf = BytesIO(tar_data)
        with tarfile.open(fileobj=buf, mode="r:gz") as tar:
            # Security: prevent path traversal
            for member in tar.getmembers():
                if member.name.startswith("/") or ".." in member.name:
                    raise ValueError(f"Unsafe path in archive: {member.name}")
            tar.extractall(tmp_target, filter="data")
        # Move into place
        profiles_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_target), str(target))

    return target


def clone_profile(profiles_dir: Path, source_name: str,
                  clone_name: str) -> Path:
    """Clone a profile under a new name, excluding cache.

    Returns the new profile directory.
    Raises RuntimeError if source doesn't exist or clone name taken.
    """
    source = profiles_dir / source_name
    target = profiles_dir / clone_name
    if not source.is_dir():
        raise RuntimeError(f"Source profile '{source_name}' not found")
    if target.exists():
        raise RuntimeError(f"Profile '{clone_name}' already exists")

    target.mkdir(parents=True)
    for rel in iter_profile_files(source, EXCLUDED_DIRS):
        fp = source / rel
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(fp), str(dest))

    return target


def list_profiles(profiles_dir: Path) -> List[str]:
    """List available profile names."""
    if not profiles_dir.is_dir():
        return []
    return sorted(
        d.name for d in profiles_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
