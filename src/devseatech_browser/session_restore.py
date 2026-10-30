"""AF-01: Crash Recovery & Session Restore.

Saves open-tab state periodically so the browser can offer to restore
tabs after an unexpected shutdown.  Each tab entry records its profile
name and URL — never authentication tokens or cookies, so restoring a
tab re-navigates without leaking cross-profile data.

Design:
  * On startup ``load_session`` checks for a non-clean previous exit.
  * ``save_session`` is called on a QTimer every ``SAVE_INTERVAL_MS`` and
    on clean exit (``mark_clean``).
  * ``mark_clean`` writes ``{"clean": true}`` so the next launch knows
    the previous session ended normally.
  * The session file is written atomically (temp → fsync → replace) to
    survive mid-write crashes.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

# How often (ms) the running browser auto-saves its tab state.
SAVE_INTERVAL_MS = 30_000  # 30 seconds

# Maximum tabs we persist (sanity guard).
MAX_TABS = 500


@dataclass(frozen=True)
class TabEntry:
    """One open tab to persist."""
    profile: str
    url: str
    title: str = ""


def _session_path(app_dir: Path) -> Path:
    return app_dir / "session.json"


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write *data* as JSON atomically (temp+fsync+replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(tmp, 0o600)
    tmp.replace(path)


# ── public API ───────────────────────────────────────────────────────

def save_session(app_dir: Path, tabs: List[TabEntry]) -> None:
    """Persist the current set of open tabs.

    Marks the session as *unclean* (``clean: false``) so that an
    unexpected exit is detectable on the next launch.
    """
    entries = [asdict(t) for t in tabs[:MAX_TABS]]
    data = {
        "clean": False,
        "saved_at": time.time(),
        "tabs": entries,
    }
    _atomic_write_json(_session_path(app_dir), data)


def mark_clean(app_dir: Path) -> None:
    """Called on intentional exit to mark the session as cleanly closed."""
    _atomic_write_json(_session_path(app_dir), {"clean": True, "tabs": []})


def load_session(app_dir: Path) -> Optional[List[TabEntry]]:
    """Return saved tabs if the previous exit was unclean.

    Returns ``None`` when the last session exited cleanly or no state
    file exists.  Silently returns ``None`` on corruption (fail-open:
    the user just loses the restore offer, no crash).
    """
    path = _session_path(app_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if data.get("clean", True):
        return None
    tabs: list[TabEntry] = []
    for entry in data.get("tabs", []):
        if not isinstance(entry, dict):
            continue
        profile = entry.get("profile", "")
        url = entry.get("url", "")
        if not profile or not url:
            continue
        tabs.append(TabEntry(
            profile=str(profile),
            url=str(url),
            title=str(entry.get("title", "")),
        ))
    return tabs if tabs else None


def needs_restore(app_dir: Path) -> bool:
    """Quick check: was the last exit unclean?"""
    return load_session(app_dir) is not None
