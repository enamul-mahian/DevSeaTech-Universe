"""AF-16: Keyboard Shortcuts Manager.

Customizable shortcuts with conflict validation and accessibility.

Design:
  * ``Shortcut`` binds a key combo to an action.
  * ``ShortcutStore`` persists per-profile shortcuts as JSON.
  * ``validate_shortcuts`` detects conflicts.
  * Default shortcuts provided; user overrides layer on top.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Shortcut:
    """A keyboard shortcut binding."""
    action: str          # e.g. "new_tab", "close_tab"
    keys: str            # e.g. "Ctrl+T", "Ctrl+W"
    description: str = ""
    enabled: bool = True
    custom: bool = False  # True if user-modified

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Shortcut":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


# ── default shortcuts ──────────────────────────────────────────────

DEFAULT_SHORTCUTS: List[Shortcut] = [
    Shortcut("new_tab", "Ctrl+T", "Open a new tab"),
    Shortcut("close_tab", "Ctrl+W", "Close current tab"),
    Shortcut("reload", "Ctrl+R", "Reload page"),
    Shortcut("hard_reload", "Ctrl+Shift+R", "Hard reload (bypass cache)"),
    Shortcut("back", "Alt+Left", "Go back"),
    Shortcut("forward", "Alt+Right", "Go forward"),
    Shortcut("find", "Ctrl+F", "Find on page"),
    Shortcut("zoom_in", "Ctrl+=", "Zoom in"),
    Shortcut("zoom_out", "Ctrl+-", "Zoom out"),
    Shortcut("zoom_reset", "Ctrl+0", "Reset zoom"),
    Shortcut("fullscreen", "F11", "Toggle fullscreen"),
    Shortcut("dev_tools", "F12", "Open developer tools"),
    Shortcut("address_bar", "Ctrl+L", "Focus address bar"),
    Shortcut("downloads", "Ctrl+J", "Open downloads"),
    Shortcut("history", "Ctrl+H", "Open history"),
]


@dataclass(frozen=True)
class ShortcutConflict:
    """A detected shortcut conflict."""
    keys: str
    actions: Tuple[str, ...]
    message: str


SHORTCUTS_FILE = "shortcuts.json"


class ShortcutStore:
    """Per-profile shortcut storage with conflict detection."""

    def __init__(self, profile_dir: Path):
        self._profile_dir = profile_dir
        self._path = profile_dir / "storage" / SHORTCUTS_FILE
        self._shortcuts: Dict[str, Shortcut] = {}
        self._load_defaults()
        self._load_custom()

    def _load_defaults(self) -> None:
        for sc in DEFAULT_SHORTCUTS:
            self._shortcuts[sc.action] = Shortcut(
                sc.action, sc.keys, sc.description, sc.enabled, False)

    def _load_custom(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text())
            for item in data.get("shortcuts", []):
                sc = Shortcut.from_dict(item)
                sc.custom = True
                self._shortcuts[sc.action] = sc
        except (json.JSONDecodeError, KeyError):
            pass

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        custom = [s.to_dict() for s in self._shortcuts.values() if s.custom]
        data = {"shortcuts": custom}
        self._path.write_text(json.dumps(data, indent=2))

    def get(self, action: str) -> Optional[Shortcut]:
        return self._shortcuts.get(action)

    def set_keys(self, action: str, keys: str) -> None:
        """Set or override the key binding for an action."""
        if action in self._shortcuts:
            sc = self._shortcuts[action]
            self._shortcuts[action] = Shortcut(
                action, keys, sc.description, sc.enabled, True)
        else:
            self._shortcuts[action] = Shortcut(action, keys, custom=True)
        self._save()

    def reset(self, action: str) -> bool:
        """Reset an action to its default shortcut."""
        default = {s.action: s for s in DEFAULT_SHORTCUTS}
        if action in default:
            self._shortcuts[action] = Shortcut(
                default[action].action, default[action].keys,
                default[action].description)
            self._save()
            return True
        return False

    def reset_all(self) -> None:
        """Reset all shortcuts to defaults."""
        self._shortcuts.clear()
        self._load_defaults()
        # Remove custom file
        if self._path.exists():
            self._path.unlink()

    def list_all(self) -> List[Shortcut]:
        return list(self._shortcuts.values())

    def list_enabled(self) -> List[Shortcut]:
        return [s for s in self._shortcuts.values() if s.enabled]

    def find_by_keys(self, keys: str) -> List[Shortcut]:
        """Find all shortcuts using the given key combo."""
        return [s for s in self._shortcuts.values()
                if s.keys.lower() == keys.lower() and s.enabled]

    def validate(self) -> List[ShortcutConflict]:
        """Detect conflicting shortcuts."""
        by_keys: Dict[str, List[str]] = {}
        for sc in self._shortcuts.values():
            if not sc.enabled:
                continue
            key = sc.keys.lower()
            by_keys.setdefault(key, []).append(sc.action)
        conflicts = []
        for keys, actions in by_keys.items():
            if len(actions) > 1:
                conflicts.append(ShortcutConflict(
                    keys, tuple(actions),
                    f"Key '{keys}' bound to: {', '.join(actions)}"))
        return conflicts

    def count(self) -> int:
        return len(self._shortcuts)
