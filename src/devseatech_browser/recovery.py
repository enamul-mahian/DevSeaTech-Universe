"""Explicit local-owner recovery for the development preview only.

This module is not a secure production identity recovery mechanism.
It preserves browser profiles and archives the previous auth configuration.
"""
from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_APP_DIR = Path.home() / ".devseatech-browser"


def archive_preview_auth(app_dir: Path, confirmation: str) -> Path:
    """Move auth.json to a non-overwriting local archive. Never touch profiles."""
    if confirmation != "RESET DEVELOPMENT PREVIEW LOGIN":
        raise ValueError("Recovery confirmation does not match.")
    auth = app_dir / "auth.json"
    if not auth.is_file() or auth.is_symlink():
        raise FileNotFoundError("No regular auth.json found; nothing changed.")
    archive_dir = app_dir / "recovery-backups"
    archive_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = archive_dir / f"auth-{stamp}.json"
    # Exclusive destination creation avoids silently overwriting old backups.
    with destination.open("xb") as out_file, auth.open("rb") as in_file:
        shutil.copyfileobj(in_file, out_file)
    os.chmod(destination, 0o600)
    auth.unlink()
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local login reset for DevSeaTech development preview only."
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_APP_DIR)
    args = parser.parse_args()
    print("Close DevSeaTech Browser before continuing.")
    print("This is NOT verified account recovery. Run only as the authorized")
    print("device owner under the original operating-system account.")
    print("This archives local authentication settings; existing profiles")
    print("and cookies are not intentionally changed, but login continuity")
    print("and any future encrypted data are NOT guaranteed.")
    confirm = input("Type RESET DEVELOPMENT PREVIEW LOGIN to continue: ")
    try:
        saved = archive_preview_auth(args.data_dir, confirm)
    except (ValueError, OSError) as error:
        print(f"Reset cancelled: {error}")
        return 1
    print(f"Previous authentication settings archived: {saved}")
    print("Restart the preview and create new master and admin passwords.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
