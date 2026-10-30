"""AF-04: Engine Compatibility Checker.

Checks runtime environment, storage schema, OS compatibility and sandbox
requirements before the browser starts or before an engine switch.

Checks:
  1. Python version >= 3.10
  2. PySide6 importable and version adequate
  3. Qt WebEngine runtime available
  4. OS platform supported (Windows/Linux)
  5. OpenGL / display server availability (Linux: X11 or Wayland)
  6. Sandbox requirements (non-root on Linux, or sandbox disabled flag)
  7. Disk space for profiles directory
  8. Storage schema version compatibility

All checks are read-only and non-destructive.
"""
from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class CheckResult(str, Enum):
    OK = "ok"
    WARNING = "warning"
    FAIL = "fail"


@dataclass(frozen=True)
class CompatCheck:
    name: str
    result: CheckResult
    detail: str


# Minimum free disk (bytes) before we warn.
MIN_FREE_DISK_BYTES = 100 * 1024 * 1024  # 100 MiB

# Minimum PySide6 version we support.
MIN_PYSIDE6_VERSION = (6, 6, 0)

SUPPORTED_PLATFORMS = ("Linux", "Windows")


def check_python_version() -> CompatCheck:
    v = sys.version_info
    if v >= (3, 10):
        return CompatCheck("Python version", CheckResult.OK,
                           f"Python {v.major}.{v.minor}.{v.micro}")
    return CompatCheck("Python version", CheckResult.FAIL,
                       f"Python {v.major}.{v.minor} — need >= 3.10")


def check_pyside6() -> CompatCheck:
    try:
        import PySide6  # noqa: F811
        from PySide6 import __version__ as pv
        parts = tuple(int(x) for x in pv.split(".")[:3])
        if parts >= MIN_PYSIDE6_VERSION:
            return CompatCheck("PySide6", CheckResult.OK, f"PySide6 {pv}")
        return CompatCheck("PySide6", CheckResult.WARNING,
                           f"PySide6 {pv} — recommend >= {'.'.join(map(str, MIN_PYSIDE6_VERSION))}")
    except ImportError:
        return CompatCheck("PySide6", CheckResult.FAIL,
                           "PySide6 not installed")


def check_webengine() -> CompatCheck:
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
        return CompatCheck("Qt WebEngine", CheckResult.OK, "Available")
    except ImportError:
        return CompatCheck("Qt WebEngine", CheckResult.FAIL,
                           "QtWebEngineWidgets not available — browser cannot start")


def check_platform() -> CompatCheck:
    plat = platform.system()
    if plat in SUPPORTED_PLATFORMS:
        return CompatCheck("Platform", CheckResult.OK, plat)
    return CompatCheck("Platform", CheckResult.WARNING,
                       f"{plat} — not officially supported (Windows/Linux only)")


def check_sandbox() -> CompatCheck:
    if platform.system() != "Linux":
        return CompatCheck("Sandbox", CheckResult.OK, "N/A (non-Linux)")
    if os.getuid() == 0:
        if os.environ.get("QTWEBENGINE_DISABLE_SANDBOX") == "1":
            return CompatCheck("Sandbox", CheckResult.WARNING,
                               "Running as root with sandbox disabled")
        return CompatCheck("Sandbox", CheckResult.FAIL,
                           "Running as root without --no-sandbox is not supported")
    return CompatCheck("Sandbox", CheckResult.OK, "Non-root user")


def check_display() -> CompatCheck:
    if platform.system() != "Linux":
        return CompatCheck("Display", CheckResult.OK, "N/A (non-Linux)")
    # offscreen mode is fine for testing
    qpa = os.environ.get("QT_QPA_PLATFORM", "")
    if qpa == "offscreen":
        return CompatCheck("Display", CheckResult.OK, "Offscreen mode")
    display = os.environ.get("DISPLAY", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")
    if display or wayland:
        server = "Wayland" if wayland else f"X11 ({display})"
        return CompatCheck("Display", CheckResult.OK, server)
    return CompatCheck("Display", CheckResult.WARNING,
                       "No DISPLAY or WAYLAND_DISPLAY — GUI may not start")


def check_disk_space(app_dir: Path) -> CompatCheck:
    target = app_dir if app_dir.exists() else Path.home()
    try:
        usage = shutil.disk_usage(target)
        free_mb = usage.free / (1024 * 1024)
        if usage.free >= MIN_FREE_DISK_BYTES:
            return CompatCheck("Disk space", CheckResult.OK,
                               f"{free_mb:.0f} MiB free")
        return CompatCheck("Disk space", CheckResult.WARNING,
                           f"Only {free_mb:.0f} MiB free — profiles may fail to save")
    except OSError as e:
        return CompatCheck("Disk space", CheckResult.WARNING, str(e))


def check_storage_schema(app_dir: Path) -> CompatCheck:
    """Check if auth.json is readable and has expected keys."""
    auth = app_dir / "auth.json"
    if not auth.exists():
        return CompatCheck("Storage schema", CheckResult.OK,
                           "First run — no existing data")
    try:
        import json
        data = json.loads(auth.read_text(encoding="utf-8"))
        required = {"master", "admin"}
        if required.issubset(data.keys()):
            return CompatCheck("Storage schema", CheckResult.OK,
                               "auth.json valid")
        missing = required - data.keys()
        return CompatCheck("Storage schema", CheckResult.WARNING,
                           f"auth.json missing keys: {', '.join(sorted(missing))}")
    except (OSError, ValueError) as e:
        return CompatCheck("Storage schema", CheckResult.FAIL,
                           f"auth.json unreadable: {e}")


# ── public API ───────────────────────────────────────────────────────

def run_all_checks(app_dir: Path) -> List[CompatCheck]:
    """Run every compatibility check and return results."""
    return [
        check_python_version(),
        check_pyside6(),
        check_webengine(),
        check_platform(),
        check_sandbox(),
        check_display(),
        check_disk_space(app_dir),
        check_storage_schema(app_dir),
    ]


def is_compatible(checks: List[CompatCheck]) -> bool:
    """True if no check returned FAIL."""
    return not any(c.result == CheckResult.FAIL for c in checks)


def format_report(checks: List[CompatCheck]) -> str:
    """Human-readable report string."""
    icons = {"ok": "✅", "warning": "⚠️", "fail": "❌"}
    lines = []
    for c in checks:
        lines.append(f"{icons[c.result.value]}  {c.name}: {c.detail}")
    return "\n".join(lines)
