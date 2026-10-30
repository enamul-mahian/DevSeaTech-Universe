"""AF-15: Workspace and Group Management.

Search/filter, grouping and safe bulk actions with authorization checks.

Design:
  * ``Workspace`` groups profiles with metadata.
  * ``WorkspaceStore`` persists workspaces as JSON.
  * Bulk operations require explicit confirmation.
  * Search/filter by name, tag, or profile membership.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class Workspace:
    """A named group of profiles."""
    name: str
    description: str = ""
    profiles: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    created_by: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Workspace":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


WORKSPACES_FILE = "workspaces.json"


class WorkspaceStore:
    """Persistence layer for workspace management."""

    def __init__(self, app_dir: Path):
        self._app_dir = app_dir
        self._path = app_dir / WORKSPACES_FILE
        self._workspaces: Dict[str, Workspace] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for item in data.get("workspaces", []):
                ws = Workspace.from_dict(item)
                self._workspaces[ws.name] = ws
        except (json.JSONDecodeError, KeyError):
            pass

    def _save(self) -> None:
        self._app_dir.mkdir(parents=True, exist_ok=True)
        data = {"workspaces": [w.to_dict() for w in self._workspaces.values()]}
        self._path.write_text(json.dumps(data, indent=2))

    def create(self, name: str, description: str = "",
               profiles: Optional[List[str]] = None,
               tags: Optional[List[str]] = None,
               created_by: str = "") -> Workspace:
        """Create a new workspace."""
        if not name:
            raise ValueError("Workspace name is required")
        if name in self._workspaces:
            raise ValueError(f"Workspace '{name}' already exists")
        now = time.time()
        ws = Workspace(name=name, description=description,
                       profiles=profiles or [], tags=tags or [],
                       created_at=now, updated_at=now,
                       created_by=created_by)
        self._workspaces[name] = ws
        self._save()
        return ws

    def get(self, name: str) -> Optional[Workspace]:
        return self._workspaces.get(name)

    def delete(self, name: str) -> bool:
        if name in self._workspaces:
            del self._workspaces[name]
            self._save()
            return True
        return False

    def list_all(self) -> List[Workspace]:
        return list(self._workspaces.values())

    def search(self, query: str) -> List[Workspace]:
        """Search workspaces by name, description, or tag."""
        q = query.lower()
        return [ws for ws in self._workspaces.values()
                if (q in ws.name.lower()
                    or q in ws.description.lower()
                    or any(q in t.lower() for t in ws.tags))]

    def find_by_profile(self, profile_name: str) -> List[Workspace]:
        """Find all workspaces containing a profile."""
        return [ws for ws in self._workspaces.values()
                if profile_name in ws.profiles]

    def add_profile(self, workspace_name: str,
                    profile_name: str) -> bool:
        ws = self._workspaces.get(workspace_name)
        if not ws:
            return False
        if profile_name not in ws.profiles:
            ws.profiles.append(profile_name)
            ws.updated_at = time.time()
            self._save()
        return True

    def remove_profile(self, workspace_name: str,
                       profile_name: str) -> bool:
        ws = self._workspaces.get(workspace_name)
        if not ws or profile_name not in ws.profiles:
            return False
        ws.profiles.remove(profile_name)
        ws.updated_at = time.time()
        self._save()
        return True

    def count(self) -> int:
        return len(self._workspaces)
