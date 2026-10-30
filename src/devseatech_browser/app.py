"""DevSeaTech Browser: Windows/Linux desktop proof of concept.

This release uses Qt WebEngine's installed runtime. It does not claim to
implement Chromium engine selection or secure enterprise deployment.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt, QLocale
from PySide6.QtWidgets import (
    QApplication, QDialog, QFormLayout, QHBoxLayout, QInputDialog,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QTabWidget,
    QToolBar, QVBoxLayout, QWidget, QLabel,
)
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from devseatech_browser.login_ui import BrandedLoginDialog
from devseatech_browser.profile_dashboard import ProfileDashboard
from devseatech_browser.recovery import archive_preview_auth
from devseatech_browser.session_restore import (
    TabEntry, save_session, mark_clean, load_session, SAVE_INTERVAL_MS,
)
from devseatech_browser.profile_health import check_all_profiles, Severity

APP_DIR = Path.home() / ".devseatech-browser"
AUTH_PATH = APP_DIR / "auth.json"
PROFILES_DIR = APP_DIR / "profiles"
DEFAULT_SESSION_MINUTES = 60


def derive_password(password: str, salt: bytes) -> str:
    return hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1
    ).hex()


def verify_password(password: str, record: dict) -> bool:
    try:
        actual = bytes.fromhex(derive_password(password, bytes.fromhex(record["salt"])))
        return secrets.compare_digest(actual, bytes.fromhex(record["hash"]))
    except (ValueError, KeyError):
        return False


def create_record(password: str) -> dict:
    salt = os.urandom(16)
    return {"salt": salt.hex(), "hash": derive_password(password, salt)}


def save_config(config: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    temp = AUTH_PATH.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(config, handle)
    os.chmod(temp, 0o600)
    temp.replace(AUTH_PATH)


def write_auth(master: str, admin: str) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "master": create_record(master),
        "admin": create_record(admin),
        "session_minutes": DEFAULT_SESSION_MINUTES,
    }
    save_config(config)


class CredentialDialog(QDialog):
    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(390)
        self.inputs = {}
        layout = QVBoxLayout(self)
        heading = QLabel("DevSeaTech  •  Secure Browser Access")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        form = QFormLayout()
        for label, secret in fields:
            entry = QLineEdit()
            if secret:
                entry.setEchoMode(QLineEdit.Password)
            form.addRow(label, entry)
            self.inputs[label] = entry
        layout.addLayout(form)
        submit = QPushButton("Continue")
        submit.clicked.connect(self.accept)
        layout.addWidget(submit)
        layout.addWidget(QLabel("www.devseatech.com  |  devseatech60@gmail.com"))
        layout.addWidget(QLabel("+8801805839123"))
    
    def values(self):
        return {label: widget.text() for label, widget in self.inputs.items()}


def setup_or_login() -> dict | None:
    if not AUTH_PATH.exists():
        dialog = BrandedLoginDialog("First-Time Setup", [
            ("Master password", True), ("Admin password", True),
        ])
        if dialog.exec() != QDialog.Accepted:
            return None
        creds = dialog.values()
        master, admin = creds["Master password"], creds["Admin password"]
        if len(master) < 12 or len(admin) < 12 or master == admin:
            QMessageBox.warning(None, "Setup rejected",
                "Use different master and administrator passwords (12+ characters each).")
            return None
        write_auth(master, admin)
    try:
        config = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError):
        QMessageBox.critical(None, "Error", "Authentication settings are unreadable.")
        return None
    for _ in range(3):
        dialog = BrandedLoginDialog("Master Login", [("Master password", True)])
        result = dialog.exec()
        if result == 2:
            choice = QMessageBox.warning(
                None, "Reset Development Preview Login",
                "This is an unverified local preview reset, NOT production recovery.\n"
                "Proceed only as the owner of this operating-system account.\n"
                "Authentication settings will be archived; profiles will be preserved.\n"
                "Existing website sessions or encrypted data may become inaccessible.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice != QMessageBox.Yes:
                return None
            phrase, confirmed = QInputDialog.getText(
                None, "Confirm Preview Reset", "Type RESET DEVELOPMENT PREVIEW LOGIN:")
            if not confirmed:
                return None
            try:
                archive_preview_auth(APP_DIR, phrase)
            except (OSError, ValueError) as exc:
                QMessageBox.critical(None, "Recovery failed", str(exc))
                return None
            QMessageBox.information(
                None, "Preview Reset",
                "Previous login configuration archived. Restart the browser to set new passwords.")
            return None
        if result != QDialog.Accepted:
            return None
        if verify_password(dialog.values()["Master password"], config["master"]):
            return config
        QMessageBox.warning(None, "Access denied", "Incorrect master password.")
    return None


class Browser(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._admin_unlocked = False  # In-memory only; reset on exit.
        self.profiles: dict[str, QWebEngineProfile] = {}
        self.setWindowTitle("DevSeaTech Universe — Development Preview")
        self.resize(1220, 790)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)
        back = toolbar.addAction("Back")
        back.triggered.connect(lambda: self.current_action("back"))
        forward = toolbar.addAction("Forward")
        forward.triggered.connect(lambda: self.current_action("forward"))
        reload_action = toolbar.addAction("Reload")
        reload_action.triggered.connect(lambda: self.current_action("reload"))
        self.address = QLineEdit()
        self.address.setPlaceholderText("Enter a website URL")
        self.address.returnPressed.connect(self.navigate)
        toolbar.addWidget(self.address)
        new_tab = toolbar.addAction("New Tab")
        new_tab.triggered.connect(lambda: self.add_tab("Default"))
        new_profile = toolbar.addAction("New Profile")
        new_profile.triggered.connect(self.create_profile)
        settings = toolbar.addAction("Session Settings")
        settings.triggered.connect(self.configure_timer)
        dashboard = toolbar.addAction("Profiles Dashboard")
        dashboard.triggered.connect(self.open_profiles_dashboard)
        health = toolbar.addAction("Health Check")
        health.triggered.connect(self.run_health_check)
        self.tabs.currentChanged.connect(self.update_address)
        self.add_tab("Default")
        minutes = max(1, min(int(config.get("session_minutes", 60)), 1440))
        self.deadline = datetime.now() + timedelta(minutes=minutes)
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.check_deadline)
        self.session_timer.start(1000)
        self.statusBar().showMessage(f"Session duration: {minutes} minutes")

        # AF-01: periodic session state save
        self._save_timer = QTimer(self)
        self._save_timer.timeout.connect(self._auto_save_session)
        self._save_timer.start(SAVE_INTERVAL_MS)
        self._auto_save_session()  # immediate first save

    # ── AF-01 session restore helpers ────────────────────────────────

    def _collect_tabs(self) -> list[TabEntry]:
        entries: list[TabEntry] = []
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i)
            if view is None:
                continue
            url = view.url().toString() if view.url() else ""
            title = self.tabs.tabText(i)
            # Recover profile name from the tab title prefix ("Profile: title")
            profile = "Default"
            if ": " in title:
                profile = title.split(": ", 1)[0]
            entries.append(TabEntry(profile=profile, url=url, title=title))
        return entries

    def _auto_save_session(self) -> None:
        save_session(APP_DIR, self._collect_tabs())

    def closeEvent(self, event):  # noqa: N802 — Qt naming
        """Mark session clean on intentional close."""
        self._save_timer.stop()
        mark_clean(APP_DIR)
        super().closeEvent(event)

    @staticmethod
    def restore_tabs_from(app_dir: Path) -> list[TabEntry] | None:
        """Return tabs from a previous unclean exit, or None."""
        return load_session(app_dir)

    def open_profiles_dashboard(self) -> None:
        """Inspect and open existing profiles without modifying their data."""
        ProfileDashboard(PROFILES_DIR, lambda name: self.add_tab(name), self).exec()

    # ── AF-03 profile health check ───────────────────────────────────

    def run_health_check(self) -> None:
        """Show a dialog with profile health findings."""
        findings = check_all_profiles(PROFILES_DIR)
        lines: list[str] = []
        for f in findings:
            icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(
                f.severity.value, "•")
            lines.append(f"{icon}  [{f.profile}] {f.code}: {f.message}")
        text = "\n".join(lines) if lines else "All profiles healthy."
        has_errors = any(f.severity == Severity.ERROR for f in findings)
        if has_errors:
            QMessageBox.warning(self, "Profile Health Check", text)
        else:
            QMessageBox.information(self, "Profile Health Check", text)

    def profile_for(self, name: str) -> QWebEngineProfile:
        if name in self.profiles:
            return self.profiles[name]
        profile_path = PROFILES_DIR / name
        profile_path.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile(name, self)
        profile.setPersistentStoragePath(str(profile_path / "storage"))
        profile.setCachePath(str(profile_path / "cache"))
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
        self.profiles[name] = profile
        return profile

    def add_tab(self, profile_name: str, url: str = "https://www.google.com"):
        view = QWebEngineView(self)
        page = QWebEnginePage(self.profile_for(profile_name), view)
        view.setPage(page)
        index = self.tabs.addTab(view, profile_name)
        view.titleChanged.connect(
            lambda title, v=view, p=profile_name: self.set_tab_title(v, p, title))
        view.urlChanged.connect(lambda _url, v=view: self.update_view_address(v))
        self.tabs.setCurrentIndex(index)
        view.setUrl(QUrl(url))

    def set_tab_title(self, view, profile, title):
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, f"{profile}: {title[:30]}")

    def current_action(self, method):
        view = self.tabs.currentWidget()
        if view is not None:
            getattr(view, method)()

    def navigate(self):
        value = self.address.text().strip()
        if not value:
            return
        if "://" not in value:
            value = "https://" + value
        view = self.tabs.currentWidget()
        if view:
            view.setUrl(QUrl(value))

    def update_view_address(self, view):
        if self.tabs.currentWidget() is view:
            self.address.setText(view.url().toString())

    def update_address(self, _index):
        view = self.tabs.currentWidget()
        self.address.setText(view.url().toString() if view else "")

    def close_tab(self, index):
        view = self.tabs.widget(index)
        self.tabs.removeTab(index)
        view.deleteLater()
        if self.tabs.count() == 0:
            self.close()

    def admin_confirmed(self) -> bool:
        if self._admin_unlocked:
            return True
        dialog = CredentialDialog("Unlock Admin for This Session",
                                  [("Administrator password", True)], self)
        verified = (dialog.exec() == QDialog.Accepted
                    and verify_password(dialog.values()["Administrator password"],
                                        self.config["admin"]))
        if verified:
            self._admin_unlocked = True
            self.statusBar().showMessage(
                "Administrator unlocked for this browser session.")
        return verified

    def configure_timer(self):
        if not self.admin_confirmed():
            QMessageBox.warning(self, "Denied", "Administrator authorization required.")
            return
        current = max(1, min(int(self.config.get("session_minutes", 60)), 1440))
        minutes, ok = QInputDialog.getInt(
            self, "Session Settings", "Session duration (minutes):",
            current, 1, 1440, 1)
        if not ok:
            return
        self.config["session_minutes"] = minutes
        save_config(self.config)
        self.statusBar().showMessage(
            f"Saved: {minutes} minutes per login. Applies on next login.")
        QMessageBox.information(self, "Saved",
            "New session duration will apply after the next master login.")

    def create_profile(self):
        if not self.admin_confirmed():
            QMessageBox.warning(self, "Denied", "Administrator authorization required.")
            return
        name, ok = QInputDialog.getText(self, "Create Profile", "Profile name (letters, numbers, - or _):")
        if not ok:
            return
        if not name or len(name) > 40 or not all(c.isalnum() or c in "-_" for c in name):
            QMessageBox.warning(self, "Invalid name", "Use 1–40 letters, numbers, hyphens or underscores.")
            return
        self.add_tab(name)

    def check_deadline(self):
        if datetime.now() >= self.deadline:
            self.session_timer.stop()
            QMessageBox.information(self, "Session expired", "Your permitted session has ended.")
            self.close()


def main():
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
    app = QApplication(sys.argv)
    app.setStyleSheet("""
      QWidget { background: #09162c; color: #e4f7ff; font-size: 13px; }
      QLineEdit { background: #102947; border: 1px solid #23afd2;
                  border-radius: 6px; padding: 9px; }
      QPushButton { background: #086da2; padding: 10px; border-radius: 6px; }
      QPushButton:hover { background: #0c9ecd; }
      QTabBar::tab:selected { background: #075d90; }
      QTabBar::tab { padding: 9px; }
      QLabel#heading { color: #36e6ff; font-size: 19px; font-weight: bold; }
    """)
    config = setup_or_login()
    if not config:
        return 1
    # Read crash-recovery state BEFORE constructing Browser. Browser starts
    # its periodic save loop in __init__, so constructing it first would
    # overwrite the previous unclean session before we could restore it.
    saved_tabs = Browser.restore_tabs_from(APP_DIR)
    window = Browser(config)

    if saved_tabs:
        choice = QMessageBox.question(
            window, "Restore Previous Session",
            f"The previous session did not close normally.\n"
            f"Restore {len(saved_tabs)} tab(s)?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if choice == QMessageBox.Yes:
            # The fresh window opens a default tab. Replace it when restoring
            # to avoid silently duplicating tabs on every crash recovery.
            for index, tab in enumerate(saved_tabs):
                if index == 0 and window.tabs.count() == 1:
                    window.tabs.removeTab(0)
                window.add_tab(tab.profile, tab.url)
    # Persist the user-selected tab set; the next unclean exit can recover it.
    window._auto_save_session()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
