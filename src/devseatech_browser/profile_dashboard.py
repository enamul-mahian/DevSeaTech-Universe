"""Read-only profile dashboard for the desktop development preview.

Profiles are discovered from disk; opening a profile uses the existing Browser
tab API. No profile or credential files are modified by the dashboard.
"""
from __future__ import annotations

from pathlib import Path
from devseatech_browser.profile_restore import restore_as_new_profile
from devseatech_browser.profile_listing import list_profiles
from devseatech_browser.backup import create_backup

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QLabel, QInputDialog, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)




class ProfileDashboard(QDialog):
    """First functional iteration of the approved profile management design."""

    def __init__(self, profiles_dir: Path, open_profile, parent=None, create_profile=None, is_profile_active=None):
        super().__init__(parent)
        self.profiles_dir = profiles_dir
        self.open_profile = open_profile
        self.create_profile = create_profile
        self.is_profile_active = is_profile_active
        self.setWindowTitle("DevSeaTech Universe — Profiles")
        self.resize(850, 540)
        self.setMinimumSize(640, 400)
        self.setStyleSheet("""
            QDialog { background: #071327; color: #eef8ff; }
            QLabel { color: #d7eafa; font-size: 14px; }
            QLineEdit { background: #102844; border: 1px solid #296e9b;
                        border-radius: 7px; color: white; padding: 9px; }
            QTableWidget { background: #0b203b; color: #e6f5ff;
                           gridline-color: #24435c; selection-background-color: #165a91; }
            QHeaderView::section { background: #123454; color: #dff8ff; padding: 9px; }
            QPushButton { background: #0869a3; color: white;
                          padding: 9px 18px; border-radius: 7px; }
        """)
        layout = QVBoxLayout(self)
        heading = QLabel("PROFILE MANAGEMENT")
        heading.setStyleSheet("font-size: 22px; font-weight: 700; color: #65dcff;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Select a profile to open it in an isolated browser tab."))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search profiles")
        self.search.textChanged.connect(self.refresh)
        layout.addWidget(self.search)
        self.empty_state = QLabel()
        self.empty_state.setWordWrap(True)
        layout.addWidget(self.empty_state)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Profile", "Storage"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(lambda row, _col: self.activate(row))
        self.table.itemSelectionChanged.connect(self._update_selection)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        buttons.addWidget(refresh_button)
        if self.create_profile is not None:
            create_button = QPushButton("Create Profile")
            create_button.clicked.connect(self.create_new_profile)
            buttons.addWidget(create_button)
        backup_button = QPushButton("Encrypted Backup")
        backup_button.clicked.connect(self.backup_selected)
        buttons.addWidget(backup_button)
        restore_button = QPushButton("Restore as New Profile")
        restore_button.clicked.connect(self.restore_new_profile)
        buttons.addWidget(restore_button)
        buttons.addStretch()
        self.open_button = QPushButton("Open Selected Profile")
        self.open_button.clicked.connect(self.open_selected)
        self.open_button.setEnabled(False)
        buttons.addWidget(self.open_button)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self, _value=None):
        all_names = list_profiles(self.profiles_dir)
        names = [
            name for name in all_names
            if self.search.text().casefold() in name.casefold()
        ]
        self.table.setRowCount(len(names))
        for row, name in enumerate(names):
            item = QTableWidgetItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, QTableWidgetItem("Local profile"))
        self.table.resizeColumnToContents(0)
        if names:
            self.empty_state.hide()
        else:
            self.empty_state.setText(
                "No profiles yet. Create a profile to get started."
                if not all_names else "No profiles match your search."
            )
            self.empty_state.show()
        self._update_selection()

    def _update_selection(self):
        self.open_button.setEnabled(self.table.currentRow() >= 0)

    def activate(self, row: int):
        item = self.table.item(row, 0)
        if item is None:
            return
        # Verify that a disk profile still exists; search results can go stale.
        name = item.text()
        if name not in list_profiles(self.profiles_dir):
            self.refresh()
            return
        self.open_profile(name)
        self.accept()

    def create_new_profile(self):
        """Delegate creation to Browser so existing administrator checks apply."""
        if self.create_profile is None:
            return
        self.create_profile()
        self.refresh()

    def backup_selected(self):
        """Create an encrypted snapshot only after the user confirms an inactive profile."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Profile", "Select a profile to back up.")
            return
        item = self.table.item(row, 0)
        if item is None or item.text() not in list_profiles(self.profiles_dir):
            QMessageBox.warning(self, "Unavailable", "Selected profile no longer exists.")
            self.refresh()
            return
        name = item.text()
        if self.is_profile_active is None or self.is_profile_active(name):
            QMessageBox.warning(
                self, "Profile In Use",
                "Cannot back up an open or unverified profile. "
                "Close all browser tabs for this profile and try again.",
            )
            return
        secret, ok = QInputDialog.getText(
            self, "Encrypt Profile Backup", "Backup passphrase (12+ characters):",
            QLineEdit.Password,
        )
        if not ok:
            return
        if len(secret) < 12:
            QMessageBox.warning(self, "Weak Passphrase", "Use at least 12 characters.")
            return
        try:
            destination = create_backup(
                self.profiles_dir / name,
                self.profiles_dir.parent / "backups" / name,
                secret,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Backup Failed", str(exc))
            return
        finally:
            secret = ""
        QMessageBox.information(
            self, "Backup Complete",
            "Encrypted snapshot saved to:\\n" + str(destination)
            + "\\nKeep the passphrase safe; it cannot be recovered.",
        )

    def restore_new_profile(self):
        """Never overwrite an existing profile while restoring a snapshot."""
        path, _filter = QFileDialog.getOpenFileName(
            self, "Select Encrypted Backup", str(self.profiles_dir.parent / "backups"),
            "DevSeaTech Backup (*.dstbak)",
        )
        if not path:
            return
        name, ok = QInputDialog.getText(
            self, "New Profile Name", "Name for the restored profile:",
        )
        if not ok:
            return
        secret, ok = QInputDialog.getText(
            self, "Decrypt Backup", "Backup passphrase:", QLineEdit.Password,
        )
        if not ok:
            return
        try:
            target = restore_as_new_profile(
                Path(path), secret, self.profiles_dir, name.strip(),
            )
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Restore Failed", str(exc))
            return
        finally:
            secret = ""
        self.refresh()
        QMessageBox.information(
            self, "Restore Complete",
            "Restored to a new profile: " + target.name
            + "\\nWebsite sessions may require signing in again.",
        )

    def open_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.activate(row)
