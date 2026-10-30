"""AF-03: Profile Health Check.

Non-destructive diagnostic scan of browser profiles.  Reports
actionable findings without modifying or deleting any data.

Checks performed per profile:
  1. Directory exists and is readable.
  2. ``storage/`` subdirectory present.
  3. ``cache/`` subdirectory present (advisory — cache is regenerated).
  4. No unexpected symlinks inside the profile tree (possible escape).
  5. Total profile size within a configurable limit.
  6. Cookie database is a valid SQLite file (header magic bytes).

The public entry point is ``check_all_profiles`` which returns a list
of ``Finding`` dataclasses.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

# SQLite files start with this 16-byte header.
_SQLITE_MAGIC = b"SQLite format 3\x00"

# Default maximum profile size (bytes) before we warn.
DEFAULT_MAX_PROFILE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    """One diagnostic finding."""
    profile: str
    severity: Severity
    code: str
    message: str


# ── individual checks ────────────────────────────────────────────────

def _check_directory_readable(profile_dir: Path, name: str) -> List[Finding]:
    if not profile_dir.is_dir():
        return [Finding(name, Severity.ERROR, "DIR_MISSING",
                        f"Profile directory does not exist: {profile_dir}")]
    try:
        list(profile_dir.iterdir())
    except PermissionError:
        return [Finding(name, Severity.ERROR, "DIR_UNREADABLE",
                        f"Cannot read profile directory: {profile_dir}")]
    return []


def _check_subdirectory(profile_dir: Path, name: str, subdir: str,
                        severity: Severity) -> List[Finding]:
    p = profile_dir / subdir
    if not p.is_dir():
        return [Finding(name, severity, f"{subdir.upper()}_MISSING",
                        f"Expected subdirectory '{subdir}' not found in profile.")]
    return []


def _check_symlinks(profile_dir: Path, name: str) -> List[Finding]:
    """Warn on any symlinks inside the profile tree."""
    findings: list[Finding] = []
    try:
        for root, dirs, files in os.walk(profile_dir, followlinks=False):
            for entry in dirs + files:
                full = Path(root) / entry
                if full.is_symlink():
                    findings.append(Finding(
                        name, Severity.WARNING, "SYMLINK_FOUND",
                        f"Symlink detected: {full.relative_to(profile_dir)}"))
    except OSError:
        findings.append(Finding(name, Severity.WARNING, "WALK_ERROR",
                                "Could not fully scan profile for symlinks."))
    return findings


def _check_size(profile_dir: Path, name: str,
                max_bytes: int) -> List[Finding]:
    total = 0
    try:
        for root, _dirs, files in os.walk(profile_dir, followlinks=False):
            for f in files:
                try:
                    total += (Path(root) / f).stat().st_size
                except OSError:
                    pass
    except OSError:
        return [Finding(name, Severity.WARNING, "SIZE_SCAN_ERROR",
                        "Could not fully calculate profile size.")]
    if total > max_bytes:
        mb = total / (1024 * 1024)
        limit_mb = max_bytes / (1024 * 1024)
        return [Finding(name, Severity.WARNING, "SIZE_EXCEEDED",
                        f"Profile is {mb:.0f} MiB (limit {limit_mb:.0f} MiB).")]
    return []


def _check_cookie_db(profile_dir: Path, name: str) -> List[Finding]:
    """Check if the Cookies file (if present) has valid SQLite magic."""
    cookies = profile_dir / "storage" / "Cookies"
    if not cookies.exists():
        return []  # no cookies yet — fine
    try:
        with cookies.open("rb") as fh:
            header = fh.read(16)
    except OSError:
        return [Finding(name, Severity.ERROR, "COOKIE_UNREADABLE",
                        "Cookies file exists but cannot be read.")]
    if header != _SQLITE_MAGIC:
        return [Finding(name, Severity.ERROR, "COOKIE_CORRUPT",
                        "Cookies file does not appear to be a valid SQLite database.")]
    return []


# ── public API ───────────────────────────────────────────────────────

def check_profile(profile_dir: Path, name: str, *,
                  max_bytes: int = DEFAULT_MAX_PROFILE_BYTES) -> List[Finding]:
    """Run all health checks on a single profile and return findings."""
    findings: list[Finding] = []
    findings.extend(_check_directory_readable(profile_dir, name))
    if findings:
        return findings  # cannot continue if directory is broken
    findings.extend(_check_subdirectory(profile_dir, name, "storage", Severity.WARNING))
    findings.extend(_check_subdirectory(profile_dir, name, "cache", Severity.INFO))
    findings.extend(_check_symlinks(profile_dir, name))
    findings.extend(_check_size(profile_dir, name, max_bytes))
    findings.extend(_check_cookie_db(profile_dir, name))
    return findings


def check_all_profiles(profiles_dir: Path, *,
                       max_bytes: int = DEFAULT_MAX_PROFILE_BYTES,
                       ) -> List[Finding]:
    """Scan every profile under *profiles_dir* and return all findings.

    If *profiles_dir* itself doesn't exist, returns a single ERROR
    finding.
    """
    if not profiles_dir.is_dir():
        return [Finding("(global)", Severity.ERROR, "PROFILES_DIR_MISSING",
                        f"Profiles directory does not exist: {profiles_dir}")]
    findings: list[Finding] = []
    for entry in sorted(profiles_dir.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            findings.extend(check_profile(entry, entry.name,
                                          max_bytes=max_bytes))
    if not findings:
        findings.append(Finding("(all)", Severity.INFO, "ALL_OK",
                                "All profiles passed health checks."))
    return findings
