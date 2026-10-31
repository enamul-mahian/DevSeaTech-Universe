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
        from PySide6.QtWidgets import (
            QApplication, QDialog, QLineEdit, QPushButton, QWidget,
        )
        from PySide6.QtCore import QTimer
    except Exception as exc:  # noqa: BLE001
        fail(f"PySide6 import failed: {exc}")

    app = QApplication.instance() or QApplication([])

    # 1. Login dialog constructs.
    try:
        from devseatech_browser.login_ui import BrandedLoginDialog

        dialog = BrandedLoginDialog("Master Login", [("Master password", True)])
        assert dialog.inputs, "login dialog has no input fields"
        # Force the actual Qt paint path; construction alone missed a crash.
        dialog.show()
        app.processEvents()
        background = dialog.findChild(QWidget, "galaxy")
        assert background is not None, "login canvas missing"
        from PySide6.QtGui import QPixmap
        image = QPixmap(background.size())
        background.render(image)
        assert not image.isNull(), "login canvas failed to render"
        dialog.hide()
        password = dialog.inputs["Master password"]
        visibility = dialog.findChild(QPushButton, "passwordVisibility")
        assert visibility is not None, "password visibility control is missing"
        assert password.echoMode() == QLineEdit.Password, "password is not hidden by default"
        visibility.click()
        assert password.echoMode() == QLineEdit.Normal, "password did not become visible"
        visibility.click()
        assert password.echoMode() == QLineEdit.Password, "password did not become hidden again"
    except Exception as exc:  # noqa: BLE001
        fail(f"login dialog construction or interaction failed: {exc}")

    # 2. Dashboard controls cover filtering, empty state, creation and opening.
    try:
        from devseatech_browser.profile_dashboard import ProfileDashboard

        with tempfile.TemporaryDirectory() as profile_root:
            profiles_dir = Path(profile_root)
            empty_dashboard = ProfileDashboard(profiles_dir, lambda _name: None)
            assert empty_dashboard.table.rowCount() == 0, "empty store is not empty"
            assert empty_dashboard.empty_state.text() == (
                "No profiles yet. Create a profile to get started."
            ), "empty profile store has no guidance"
            empty_dashboard.close()

            (profiles_dir / "Existing").mkdir()
            opened = []

            def create_profile():
                (profiles_dir / "Created").mkdir()

            dashboard = ProfileDashboard(
                profiles_dir, opened.append, create_profile=create_profile
            )
            assert dashboard.table.rowCount() == 1, "existing profile was not listed"
            assert not dashboard.open_button.isEnabled(), "open enabled without selection"
            dashboard.search.setText("missing")
            assert dashboard.table.rowCount() == 0, "profile search did not filter"
            assert not dashboard.empty_state.isHidden(), "empty search state is hidden"
            dashboard.search.clear()
            create_button = next(
                button for button in dashboard.findChildren(QPushButton)
                if button.text() == "Create Profile"
            )
            create_button.click()
            assert dashboard.table.rowCount() == 2, "created profile was not refreshed"
            dashboard.table.selectRow(0)
            assert dashboard.open_button.isEnabled(), "open stayed disabled after selection"
            dashboard.open_selected()
            assert opened == ["Created"], "selected profile was not opened"
            assert dashboard.result() == QDialog.Accepted, "dashboard did not close after opening"
    except Exception as exc:  # noqa: BLE001
        fail(f"profile dashboard interaction failed: {exc}")

    # 3. Main window constructs and opens a tab (creates a QWebEngineView).
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
