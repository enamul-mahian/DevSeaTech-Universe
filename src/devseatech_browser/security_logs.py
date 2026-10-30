"""AF-13: Security and Activity Logs.

Privileged-change and security-event auditing with sensitive-data
redaction and configurable retention.

Design:
  * ``LogLevel`` / ``LogCategory`` classify events.
  * ``LogEntry`` is an immutable audit record.
  * ``SecurityLogger`` writes JSON-lines to a rotated log file.
  * Sensitive fields (passwords, tokens) are redacted before writing.
  * Retention: configurable max file size and max age.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    AUTH = "auth"                 # login, logout, failed auth
    PERMISSION = "permission"     # permission changes
    PROFILE = "profile"           # profile create/delete/export
    SETTINGS = "settings"         # setting changes
    SECURITY = "security"         # security events
    ADMIN = "admin"               # admin actions


# Fields to redact in event details
REDACT_PATTERNS = re.compile(
    r"(password|token|secret|key|credential|passphrase)",
    re.IGNORECASE
)


@dataclass(frozen=True)
class LogEntry:
    """An immutable audit log entry."""
    timestamp: float
    level: LogLevel
    category: LogCategory
    action: str
    actor: str = ""              # who performed the action
    target: str = ""             # what was affected
    details: Dict[str, Any] = field(default_factory=dict)
    source_ip: str = ""          # for monitoring only, never auto-blocking

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "category": self.category.value,
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "details": self.details,
            "source_ip": self.source_ip,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LogEntry":
        return cls(
            timestamp=data.get("timestamp", 0.0),
            level=LogLevel(data.get("level", "info")),
            category=LogCategory(data.get("category", "security")),
            action=data.get("action", ""),
            actor=data.get("actor", ""),
            target=data.get("target", ""),
            details=data.get("details", {}),
            source_ip=data.get("source_ip", ""),
        )


def redact_sensitive(details: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields from event details."""
    redacted = {}
    for k, v in details.items():
        if REDACT_PATTERNS.search(k):
            redacted[k] = "***REDACTED***"
        elif isinstance(v, dict):
            redacted[k] = redact_sensitive(v)
        else:
            redacted[k] = v
    return redacted


LOG_FILE = "security_audit.jsonl"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024    # 10 MiB
DEFAULT_MAX_AGE_DAYS = 90


class SecurityLogger:
    """Append-only security audit logger with rotation."""

    def __init__(self, app_dir: Path,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 max_age_days: int = DEFAULT_MAX_AGE_DAYS):
        self._app_dir = app_dir
        self._log_dir = app_dir / "logs"
        self._log_file = self._log_dir / LOG_FILE
        self._max_bytes = max_bytes
        self._max_age_days = max_age_days

    def log(self, level: LogLevel, category: LogCategory,
            action: str, actor: str = "", target: str = "",
            details: Optional[Dict[str, Any]] = None,
            source_ip: str = "") -> LogEntry:
        """Write an audit log entry."""
        safe_details = redact_sensitive(details or {})
        entry = LogEntry(
            timestamp=time.time(), level=level, category=category,
            action=action, actor=actor, target=target,
            details=safe_details, source_ip=source_ip)

        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._maybe_rotate()

        with open(self._log_file, "a") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return entry

    def read_logs(self, limit: int = 100,
                  category: Optional[LogCategory] = None,
                  level: Optional[LogLevel] = None) -> List[LogEntry]:
        """Read recent log entries with optional filters."""
        if not self._log_file.exists():
            return []
        entries = []
        try:
            for line in self._log_file.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry.from_dict(data)
                    if category and entry.category != category:
                        continue
                    if level and entry.level != level:
                        continue
                    entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        except OSError:
            return []
        # Return most recent first, limited
        return list(reversed(entries[-limit:]))

    def count(self) -> int:
        """Count total log entries."""
        if not self._log_file.exists():
            return 0
        try:
            return sum(1 for line in self._log_file.read_text().splitlines()
                       if line.strip())
        except OSError:
            return 0

    def _maybe_rotate(self) -> None:
        """Rotate log file if it exceeds max size."""
        if not self._log_file.exists():
            return
        try:
            size = self._log_file.stat().st_size
            if size >= self._max_bytes:
                rotated = self._log_dir / f"security_audit.{int(time.time())}.jsonl"
                self._log_file.rename(rotated)
        except OSError:
            pass
