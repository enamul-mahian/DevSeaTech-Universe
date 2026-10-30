"""AF-05: Download Manager.

Tracks downloads initiated by the browser, provides status/history,
and handles secure destination paths.  Cancel/pause/resume are
supported only where the Qt WebEngine download API allows them.

Design:
  * ``DownloadTracker`` keeps an in-memory list of ``DownloadRecord``
    entries and persists history to a JSON file per profile.
  * Each download records: id, url, filename, destination, status,
    bytes received/total, timestamps.
  * The tracker integrates with ``QWebEngineProfile.downloadRequested``
    to intercept and manage downloads.
  * History is written atomically (same pattern as session_restore).
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class DownloadStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class DownloadRecord:
    """One download entry."""
    download_id: str
    url: str
    filename: str
    destination: str
    status: DownloadStatus = DownloadStatus.PENDING
    bytes_received: int = 0
    total_bytes: int = -1  # -1 = unknown
    started_at: float = 0.0
    finished_at: float = 0.0
    error: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "DownloadRecord":
        d = dict(d)
        d["status"] = DownloadStatus(d.get("status", "pending"))
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})


# Max history entries per profile.
MAX_HISTORY = 500

# Dangerous extensions that need extra caution.
RISKY_EXTENSIONS = frozenset({
    ".exe", ".bat", ".cmd", ".com", ".scr", ".pif", ".msi",
    ".sh", ".bash", ".csh", ".ksh",
    ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh",
    ".ps1", ".psm1", ".psd1",
})


def _history_path(profile_dir: Path) -> Path:
    return profile_dir / "download_history.json"


def _atomic_write_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def is_risky_download(filename: str) -> bool:
    """Check if a filename has a risky extension."""
    _, ext = os.path.splitext(filename.lower())
    return ext in RISKY_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Remove path separators and null bytes from a filename."""
    name = filename.replace("/", "_").replace("\\", "_").replace("\x00", "")
    if not name or name.startswith("."):
        name = "download" + ("_" + name if name else "")
    return name[:255]


class DownloadTracker:
    """Manages download records for one profile."""

    def __init__(self, profile_dir: Path):
        self._profile_dir = profile_dir
        self._records: Dict[str, DownloadRecord] = {}
        self._counter = 0
        self._load_history()

    def _load_history(self) -> None:
        path = _history_path(self._profile_dir)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                if isinstance(entry, dict):
                    rec = DownloadRecord.from_dict(entry)
                    self._records[rec.download_id] = rec
        except (OSError, ValueError, KeyError):
            pass  # corrupt history — start fresh

    def _save_history(self) -> None:
        recent = sorted(self._records.values(),
                        key=lambda r: r.started_at, reverse=True)[:MAX_HISTORY]
        _atomic_write_json(
            _history_path(self._profile_dir),
            [r.to_dict() for r in recent],
        )

    def start_download(self, url: str, filename: str,
                       destination: str) -> DownloadRecord:
        """Register a new download."""
        self._counter += 1
        did = f"dl-{self._counter}-{int(time.time())}"
        rec = DownloadRecord(
            download_id=did,
            url=url,
            filename=sanitize_filename(filename),
            destination=destination,
            status=DownloadStatus.IN_PROGRESS,
            started_at=time.time(),
        )
        self._records[did] = rec
        self._save_history()
        return rec

    def update_progress(self, download_id: str,
                        bytes_received: int, total_bytes: int) -> None:
        rec = self._records.get(download_id)
        if rec:
            rec.bytes_received = bytes_received
            rec.total_bytes = total_bytes

    def complete(self, download_id: str) -> None:
        rec = self._records.get(download_id)
        if rec:
            rec.status = DownloadStatus.COMPLETED
            rec.finished_at = time.time()
            self._save_history()

    def fail(self, download_id: str, error: str = "") -> None:
        rec = self._records.get(download_id)
        if rec:
            rec.status = DownloadStatus.FAILED
            rec.error = error
            rec.finished_at = time.time()
            self._save_history()

    def cancel(self, download_id: str) -> None:
        rec = self._records.get(download_id)
        if rec and rec.status in (DownloadStatus.IN_PROGRESS,
                                  DownloadStatus.PAUSED,
                                  DownloadStatus.PENDING):
            rec.status = DownloadStatus.CANCELLED
            rec.finished_at = time.time()
            self._save_history()

    def pause(self, download_id: str) -> None:
        rec = self._records.get(download_id)
        if rec and rec.status == DownloadStatus.IN_PROGRESS:
            rec.status = DownloadStatus.PAUSED

    def resume(self, download_id: str) -> None:
        rec = self._records.get(download_id)
        if rec and rec.status == DownloadStatus.PAUSED:
            rec.status = DownloadStatus.IN_PROGRESS

    def get(self, download_id: str) -> Optional[DownloadRecord]:
        return self._records.get(download_id)

    def list_all(self) -> List[DownloadRecord]:
        """Return all records, most recent first."""
        return sorted(self._records.values(),
                      key=lambda r: r.started_at, reverse=True)

    def active_downloads(self) -> List[DownloadRecord]:
        active = {DownloadStatus.IN_PROGRESS, DownloadStatus.PAUSED,
                  DownloadStatus.PENDING}
        return [r for r in self._records.values() if r.status in active]

    def clear_history(self) -> None:
        """Remove completed/cancelled/failed entries, keep active."""
        active = {DownloadStatus.IN_PROGRESS, DownloadStatus.PAUSED,
                  DownloadStatus.PENDING}
        self._records = {k: v for k, v in self._records.items()
                         if v.status in active}
        self._save_history()
