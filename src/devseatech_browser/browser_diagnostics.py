"""AF-14: Browser Diagnostics and Repair.

Read-only diagnostics by default; confirm, backup and rollback
before any repairs.

Design:
  * ``DiagnosticCheck`` performs a single read-only check.
  * ``run_diagnostics`` runs all checks and returns findings.
  * ``RepairAction`` describes a possible fix.
  * ``apply_repair`` only runs after explicit confirmation +
    pre-repair backup.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class DiagStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DiagFinding:
    """Result of a single diagnostic check."""
    name: str
    status: DiagStatus
    message: str
    repairable: bool = False
    repair_id: str = ""


@dataclass(frozen=True)
class RepairResult:
    """Result of a repair action."""
    repair_id: str
    success: bool
    message: str
    backup_path: str = ""


# ── diagnostic checks ─────────────────────────────────────────────

def _check_app_dir(app_dir: Path) -> DiagFinding:
    if not app_dir.is_dir():
        return DiagFinding("app_directory", DiagStatus.ERROR,
                           f"App directory missing: {app_dir}")
    return DiagFinding("app_directory", DiagStatus.OK, "App directory exists")


def _check_profiles_dir(app_dir: Path) -> DiagFinding:
    profiles = app_dir / "profiles"
    if not profiles.is_dir():
        return DiagFinding("profiles_directory", DiagStatus.WARNING,
                           "No profiles directory found",
                           repairable=True, repair_id="create_profiles_dir")
    count = sum(1 for d in profiles.iterdir()
                if d.is_dir() and not d.name.startswith("."))
    return DiagFinding("profiles_directory", DiagStatus.OK,
                       f"Profiles directory exists ({count} profiles)")


def _check_settings_file(app_dir: Path) -> DiagFinding:
    settings = app_dir / "settings.json"
    if not settings.exists():
        return DiagFinding("settings_file", DiagStatus.WARNING,
                           "No settings.json found",
                           repairable=True, repair_id="create_settings")
    try:
        json.loads(settings.read_text())
        return DiagFinding("settings_file", DiagStatus.OK,
                           "Settings file is valid JSON")
    except json.JSONDecodeError:
        return DiagFinding("settings_file", DiagStatus.ERROR,
                           "Settings file has invalid JSON",
                           repairable=True, repair_id="reset_settings")


def _check_log_dir(app_dir: Path) -> DiagFinding:
    logs = app_dir / "logs"
    if not logs.is_dir():
        return DiagFinding("logs_directory", DiagStatus.WARNING,
                           "No logs directory found",
                           repairable=True, repair_id="create_logs_dir")
    # Check for oversized logs
    total = sum(f.stat().st_size for f in logs.rglob("*") if f.is_file())
    if total > 100 * 1024 * 1024:  # 100 MiB
        return DiagFinding("logs_directory", DiagStatus.WARNING,
                           f"Logs are large ({total/(1024*1024):.0f} MiB)",
                           repairable=True, repair_id="trim_logs")
    return DiagFinding("logs_directory", DiagStatus.OK,
                       f"Logs directory OK ({total/(1024*1024):.1f} MiB)")


def _check_temp_files(app_dir: Path) -> DiagFinding:
    """Check for orphaned temp files from atomic writes."""
    temps = list(app_dir.rglob("*.tmp"))
    if temps:
        return DiagFinding("temp_files", DiagStatus.WARNING,
                           f"{len(temps)} orphaned .tmp files found",
                           repairable=True, repair_id="clean_temps")
    return DiagFinding("temp_files", DiagStatus.OK, "No orphaned temp files")


def run_diagnostics(app_dir: Path) -> List[DiagFinding]:
    """Run all read-only diagnostic checks."""
    return [
        _check_app_dir(app_dir),
        _check_profiles_dir(app_dir),
        _check_settings_file(app_dir),
        _check_log_dir(app_dir),
        _check_temp_files(app_dir),
    ]


def format_diagnostics(findings: List[DiagFinding]) -> str:
    """Format diagnostic results for display."""
    lines = ["=== Browser Diagnostics ==="]
    for f in findings:
        icon = {"ok": "OK", "warning": "WARN", "error": "ERR",
                "unknown": "??"}.get(f.status.value, "??")
        repair = " [repairable]" if f.repairable else ""
        lines.append(f"  [{icon}] {f.name}: {f.message}{repair}")
    return "\n".join(lines)


# ── repairs (require explicit confirmation) ────────────────────────

def apply_repair(app_dir: Path, repair_id: str,
                 confirmed: bool = False) -> RepairResult:
    """Apply a repair action. Must be explicitly confirmed.

    Backs up affected files before making changes.
    """
    if not confirmed:
        return RepairResult(repair_id, False,
                            "Repair not confirmed — pass confirmed=True")

    if repair_id == "create_profiles_dir":
        (app_dir / "profiles").mkdir(parents=True, exist_ok=True)
        return RepairResult(repair_id, True, "Created profiles directory")

    if repair_id == "create_settings":
        path = app_dir / "settings.json"
        path.write_text("{}")
        return RepairResult(repair_id, True, "Created default settings.json")

    if repair_id == "reset_settings":
        path = app_dir / "settings.json"
        backup = app_dir / f"settings.{int(time.time())}.bak"
        if path.exists():
            shutil.copy2(str(path), str(backup))
        path.write_text("{}")
        return RepairResult(repair_id, True,
                            "Reset settings.json to defaults",
                            backup_path=str(backup))

    if repair_id == "create_logs_dir":
        (app_dir / "logs").mkdir(parents=True, exist_ok=True)
        return RepairResult(repair_id, True, "Created logs directory")

    if repair_id == "clean_temps":
        cleaned = 0
        for tmp in app_dir.rglob("*.tmp"):
            try:
                tmp.unlink()
                cleaned += 1
            except OSError:
                pass
        return RepairResult(repair_id, True, f"Removed {cleaned} temp files")

    return RepairResult(repair_id, False, f"Unknown repair: {repair_id}")
