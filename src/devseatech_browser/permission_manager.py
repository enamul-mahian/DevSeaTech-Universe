"""AF-12: Permission Manager.

Site-by-site camera, microphone, geolocation and notifications
permissions with clear auditability.

Design:
  * ``Permission`` enum lists managed permission types.
  * ``PermissionDecision`` enum: ALLOW, DENY, ASK (default).
  * ``PermissionStore`` persists per-site decisions as JSON.
  * All decisions are explicit — no silent grants.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Permission(str, Enum):
    CAMERA = "camera"
    MICROPHONE = "microphone"
    GEOLOCATION = "geolocation"
    NOTIFICATIONS = "notifications"
    CLIPBOARD = "clipboard"
    FULLSCREEN = "fullscreen"


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"       # prompt every time (default)


@dataclass
class PermissionEntry:
    """A single permission decision for a site."""
    origin: str                  # e.g. "https://example.com"
    permission: Permission
    decision: PermissionDecision
    decided_at: float = 0.0
    decided_by: str = ""         # "user" or "admin"

    def to_dict(self) -> dict:
        return {
            "origin": self.origin,
            "permission": self.permission.value,
            "decision": self.decision.value,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PermissionEntry":
        return cls(
            origin=data["origin"],
            permission=Permission(data["permission"]),
            decision=PermissionDecision(data["decision"]),
            decided_at=data.get("decided_at", 0.0),
            decided_by=data.get("decided_by", ""),
        )


PERMISSIONS_FILE = "permissions.json"


class PermissionStore:
    """Per-profile permission storage."""

    def __init__(self, profile_dir: Path):
        self._profile_dir = profile_dir
        self._path = profile_dir / "storage" / PERMISSIONS_FILE
        self._entries: Dict[str, PermissionEntry] = {}
        self._load()

    def _key(self, origin: str, perm: Permission) -> str:
        return f"{origin}|{perm.value}"

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for item in data.get("entries", []):
                entry = PermissionEntry.from_dict(item)
                self._entries[self._key(entry.origin, entry.permission)] = entry
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"entries": [e.to_dict() for e in self._entries.values()]}
        self._path.write_text(json.dumps(data, indent=2))

    def set_permission(self, origin: str, perm: Permission,
                       decision: PermissionDecision,
                       decided_by: str = "user") -> None:
        """Set a permission decision for a site."""
        entry = PermissionEntry(
            origin=origin, permission=perm,
            decision=decision, decided_at=time.time(),
            decided_by=decided_by)
        self._entries[self._key(origin, perm)] = entry
        self._save()

    def get_decision(self, origin: str,
                     perm: Permission) -> PermissionDecision:
        """Get the current decision for a site+permission. Default: ASK."""
        key = self._key(origin, perm)
        entry = self._entries.get(key)
        return entry.decision if entry else PermissionDecision.ASK

    def get_entry(self, origin: str,
                  perm: Permission) -> Optional[PermissionEntry]:
        """Get the full entry for a site+permission."""
        return self._entries.get(self._key(origin, perm))

    def list_for_origin(self, origin: str) -> List[PermissionEntry]:
        """List all permission entries for a site."""
        return [e for e in self._entries.values() if e.origin == origin]

    def list_all(self) -> List[PermissionEntry]:
        """List all permission entries."""
        return list(self._entries.values())

    def list_origins(self) -> List[str]:
        """List all origins with stored decisions."""
        return sorted(set(e.origin for e in self._entries.values()))

    def remove(self, origin: str, perm: Permission) -> bool:
        """Remove a specific permission entry. Returns True if removed."""
        key = self._key(origin, perm)
        if key in self._entries:
            del self._entries[key]
            self._save()
            return True
        return False

    def clear_origin(self, origin: str) -> int:
        """Remove all permissions for an origin. Returns count removed."""
        to_remove = [k for k, e in self._entries.items()
                     if e.origin == origin]
        for k in to_remove:
            del self._entries[k]
        if to_remove:
            self._save()
        return len(to_remove)

    def count(self) -> int:
        return len(self._entries)
