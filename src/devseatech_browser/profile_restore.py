"""Safe encrypted backup restoration into a new, never-overwritten profile."""
from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from devseatech_browser.backup import BACKUP_SUFFIX, restore_backup

_NAME = re.compile(r"[A-Za-z0-9_-]{1,40}\Z")


def restore_as_new_profile(backup_path: Path, passphrase: str,
                           profiles_dir: Path, name: str) -> Path:
    """Validate, restore to a private staging directory, then publish once.

    An existing profile is never replaced. Failed decryption or corrupt
    archives leave the requested profile name untouched.
    """
    if not _NAME.fullmatch(name) or name in {".", ".."}:
        raise ValueError("Profile name must use 1–40 letters, digits, _ or -.")
    if backup_path.suffix != BACKUP_SUFFIX or not backup_path.is_file():
        raise ValueError("Select an existing .dstbak backup file.")
    if not passphrase:
        raise ValueError("A backup passphrase is required.")
    profiles_dir.mkdir(parents=True, exist_ok=True)
    target = profiles_dir / name
    if target.exists() or target.is_symlink():
        raise FileExistsError("A profile with this name already exists.")
    staging = Path(tempfile.mkdtemp(prefix=".restore-", dir=profiles_dir))
    try:
        restore_backup(backup_path, passphrase, staging)
        # Never overwrite even if the name was created while restoring.
        if target.exists() or target.is_symlink():
            raise FileExistsError("A profile with this name already exists.")
        staging.rename(target)
        return target
    finally:
        if staging.exists():
            shutil.rmtree(staging)
