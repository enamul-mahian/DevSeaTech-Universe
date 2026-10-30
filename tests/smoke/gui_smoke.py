"""Headless GUI runtime smoke test for the DevSeaTech desktop browser.

This is deliberately a *runtime* check, not a packaging check: it actually
constructs the Qt widgets and a Qt WebEngine view in the offscreen platform,
so it fails if the real runtime cannot start — the exact gap the owner asked
us to close ("stop treating a packaging-only CI success as runtime
verification").

It does NOT drive the interactive login (that blocks on user input). It:
  1. starts QApplication under QT_QPA_PLATFORM=offscreen,
  2. constructs the branded login dialog without executing it,
  3. constructs the main Browser window from a temporary config and asserts it
     opened at least one tab (which creates a QWebEngineView),
  4. exits 0 on success, non-zero with a message on any failure.

Run: QT_QPA_PLATFORM=offscreen PYTHONPATH=src python tests/smoke/gui_smoke.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Test-harness only: headless CI runners (and root containers) need Chromium's
# sandbox disabled and the GPU off to start. These flags are set ONLY for this
# smoke process and never in the shipped application, whose sandbox stays on.
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox --disable-gpu")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
# Keep any app data writes inside a throwaway directory.
_tmp_home = tempfile.mkdtemp(prefix="dst-smoke-home-")
os.environ["HOME"] = _tmp_home


def fail(message: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"SMOKE FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
    except Exception as exc:  # noqa: BLE001
        fail(f"PySide6 import failed: {exc}")

    app = QApplication.instance() or QApplication([])

    # 1. Login dialog constructs.
    try:
        from devseatech_browser.login_ui import BrandedLoginDialog

        dialog = BrandedLoginDialog("Master Login", [("Master password", True)])
        assert dialog.inputs, "login dialog has no input fields"
    except Exception as exc:  # noqa: BLE001
        fail(f"login dialog construction failed: {exc}")

    # 2. Main window constructs and opens a tab (creates a QWebEngineView).
    try:
        from devseatech_browser.app import Browser

        config = {"session_minutes": 1, "master": {}, "admin": {}}
        window = Browser(config)
        assert window.tabs.count() >= 1, "no browser tab was created"
    except Exception as exc:  # noqa: BLE001
        fail(f"browser window construction failed: {exc}")

    # Quit the event loop immediately; we only needed construction to succeed.
    QTimer.singleShot(0, app.quit)
    app.exec()

    print("SMOKE OK: login dialog and WebEngine-backed window constructed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
