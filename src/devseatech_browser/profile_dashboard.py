"""DevSeaTech Universe profile dashboard.

Redesigned with sidebar navigation, stats cards, and improved profile table.
Profiles are discovered from disk; opening a profile uses the existing Browser
tab API. No profile or credential files are modified by the dashboard.
"""
from __future__ import annotations

import os
from pathlib import Path
from devseatech_browser.profile_restore import restore_as_new_profile
from devseatech_browser.profile_listing import list_profiles
from devseatech_browser.backup import create_backup

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QInputDialog, QLineEdit, QMessageBox, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QGraphicsDropShadowEffect,
)


def _dir_size_mb(path: Path) -> float:
    """Calculate directory size in MB, non-recursive for speed."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file() and not entry.is_symlink():
                try:
                    total += entry.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total / (1024 * 1024)


def _stat_card(title: str, value: str, color: str = "#00d4ff") -> QFrame:
    """Create a stats card widget."""
    card = QFrame()
    card.setFixedSize(180, 100)
    card.setStyleSheet(f"""
        QFrame {{
            background: rgba(16, 41, 71, 0.8);
            border: 1px solid rgba(0, 180, 220, 0.25);
            border-radius: 12px;
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)

    val_label = QLabel(value)
    val_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; background: transparent; border: none;")
    val_label.setAlignment(Qt.AlignLeft)
    layout.addWidget(val_label)

    title_label = QLabel(title)
    title_label.setStyleSheet("font-size: 12px; color: #6fa8c8; background: transparent; border: none;")
    layout.addWidget(title_label)

    shadow = QGraphicsDropShadowEffect()
    shadow.setColor(QColor(0, 180, 220, 40))
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 4)
    card.setGraphicsEffect(shadow)
    return card


class _SidebarButton(QPushButton):
    """Styled sidebar nav button."""
    def __init__(self, text: str, icon_char: str = "", active: bool = False):
        super().__init__(f"  {icon_char}  {text}" if icon_char else f"  {text}")
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setChecked(active)
        self._update_style()
        self.toggled.connect(lambda _: self._update_style())

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 180, 220, 0.15);
                    border: none;
                    border-left: 3px solid #00d4ff;
                    color: #00d4ff;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 0;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    color: #8ab4cc;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 14px;
                    border-radius: 0;
                }
                QPushButton:hover {
                    background: rgba(0, 180, 220, 0.08);
                    color: #c8ecf8;
                }
            """)


class ProfileDashboard(QDialog):
    """Profile management dashboard with sidebar, stats, and table."""

    def __init__(self, profiles_dir: Path, open_profile, parent=None,
                 create_profile=None, is_profile_active=None):
        super().__init__(parent)
        self.profiles_dir = profiles_dir
        self.open_profile = open_profile
        self.create_profile = create_profile
        self.is_profile_active = is_profile_active
        self.setWindowTitle("DevSeaTech Universe — Dashboard")
        self.resize(1050, 640)
        self.setMinimumSize(800, 500)
        self.setStyleSheet("""
            QDialog { background: #071327; color: #eef8ff; }
        """)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ─────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background: #0a1a30;
                border-right: 1px solid rgba(0, 180, 220, 0.15);
            }
        """)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 20, 0, 20)
        sb_layout.setSpacing(2)

        # Brand
        brand = QLabel("  DevSeaTech")
        brand.setStyleSheet("font-size: 20px; font-weight: bold; color: #00d4ff; padding: 10px 16px 20px; background: transparent; border: none;")
        sb_layout.addWidget(brand)

        # Nav items
        self.nav_profiles = _SidebarButton("Profiles", "👤", active=True)
        self.nav_security = _SidebarButton("Security", "🔒")
        self.nav_settings = _SidebarButton("Settings", "⚙")
        self.nav_backups = _SidebarButton("Backups", "💾")
        self.nav_health = _SidebarButton("Health", "🏥")

        for btn in (self.nav_profiles, self.nav_security, self.nav_settings,
                     self.nav_backups, self.nav_health):
            sb_layout.addWidget(btn)

        sb_layout.addStretch()

        # Version
        ver = QLabel("  v0.1.0 — Dev Preview")
        ver.setStyleSheet("font-size: 11px; color: #3a5a6e; padding: 8px 16px; background: transparent; border: none;")
        sb_layout.addWidget(ver)

        root.addWidget(sidebar)

        # ── Main content area ───────────────────────────────────────
        main_area = QVBoxLayout()
        main_area.setContentsMargins(24, 20, 24, 20)
        main_area.setSpacing(16)

        # Header
        header = QHBoxLayout()
        heading = QLabel("Profile Management")
        heading.setStyleSheet("font-size: 24px; font-weight: 700; color: #e4f7ff;")
        header.addWidget(heading)
        header.addStretch()

        if self.create_profile is not None:
            create_btn = QPushButton("+ New Profile")
            create_btn.setStyleSheet("""
                QPushButton {
                    background: linear-gradient(135deg, #0891b2, #06b6d4);
                    color: white; padding: 10px 22px; border-radius: 8px;
                    font-size: 14px; font-weight: 600; border: none;
                }
                QPushButton:hover { background: #22d3ee; }
            """)
            create_btn.setCursor(Qt.PointingHandCursor)
            create_btn.clicked.connect(self.create_new_profile)
            header.addWidget(create_btn)
        main_area.addLayout(header)

        # Stats row
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        main_area.addLayout(self.stats_layout)

        # Search bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search profiles...")
        self.search.setStyleSheet("""
            QLineEdit {
                background: rgba(16, 41, 71, 0.85);
                border: 1px solid rgba(0, 180, 220, 0.3);
                border-radius: 10px; color: #e4f7ff;
                padding: 12px 16px; font-size: 14px;
            }
            QLineEdit:focus { border-color: #00d4ff; }
        """)
        self.search.textChanged.connect(self.refresh)
        main_area.addWidget(self.search)

        # Empty state
        self.empty_state = QLabel()
        self.empty_state.setWordWrap(True)
        self.empty_state.setStyleSheet("font-size: 15px; color: #5a8aa5; padding: 30px;")
        self.empty_state.setAlignment(Qt.AlignCenter)
        main_area.addWidget(self.empty_state)

        # Profile table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Profile", "Status", "Size", "Storage"])
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(11, 32, 59, 0.8);
                color: #e6f5ff;
                gridline-color: #1a3a54;
                border: 1px solid rgba(0, 180, 220, 0.15);
                border-radius: 10px;
                selection-background-color: rgba(0, 180, 220, 0.2);
            }
            QHeaderView::section {
                background: rgba(18, 52, 84, 0.9);
                color: #8ab4cc; padding: 10px;
                border: none;
                border-bottom: 1px solid #1a3a54;
                font-weight: 600; font-size: 12px;
                text-transform: uppercase;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected { background: rgba(0, 180, 220, 0.15); }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(lambda row, _: self.activate(row))
        self.table.itemSelectionChanged.connect(self._update_selection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableWidget { alternate-background-color: rgba(16, 41, 71, 0.4); }
        """)
        main_area.addWidget(self.table, 1)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(10)

        btn_style = """
            QPushButton {
                background: rgba(16, 41, 71, 0.8);
                border: 1px solid rgba(0, 180, 220, 0.25);
                color: #c8ecf8; padding: 10px 18px;
                border-radius: 8px; font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 180, 220, 0.15);
                border-color: #00d4ff;
            }
            QPushButton:disabled { color: #3a5a6e; border-color: #1a3a54; }
        """

        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.setStyleSheet(btn_style)
        refresh_btn.clicked.connect(self.refresh)
        actions.addWidget(refresh_btn)

        backup_btn = QPushButton("💾 Backup")
        backup_btn.setStyleSheet(btn_style)
        backup_btn.clicked.connect(self.backup_selected)
        actions.addWidget(backup_btn)

        restore_btn = QPushButton("📥 Restore")
        restore_btn.setStyleSheet(btn_style)
        restore_btn.clicked.connect(self.restore_new_profile)
        actions.addWidget(restore_btn)

        actions.addStretch()

        self.open_button = QPushButton("Open Profile →")
        self.open_button.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #0891b2, #06b6d4);
                color: white; padding: 10px 24px; border-radius: 8px;
                font-size: 14px; font-weight: 600; border: none;
            }
            QPushButton:hover { background: #22d3ee; }
            QPushButton:disabled { background: #1a3a54; color: #3a5a6e; }
        """)
        self.open_button.clicked.connect(self.open_selected)
        self.open_button.setEnabled(False)
        actions.addWidget(self.open_button)

        main_area.addLayout(actions)
        root.addLayout(main_area, 1)

    def _rebuild_stats(self, profiles: list[str]):
        """Update stats cards."""
        # Clear previous
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total = len(profiles)
        active = sum(1 for p in profiles
                     if self.is_profile_active and self.is_profile_active(p))
        total_size = 0.0
        for name in profiles:
            total_size += _dir_size_mb(self.profiles_dir / name)

        self.stats_layout.addWidget(_stat_card("Total Profiles", str(total), "#00d4ff"))
        self.stats_layout.addWidget(_stat_card("Active", str(active), "#10b981"))
        self.stats_layout.addWidget(_stat_card("Storage", f"{total_size:.1f} MB", "#f59e0b"))

        # Check for backups
        backup_dir = self.profiles_dir.parent / "backups"
        backup_count = 0
        if backup_dir.is_dir():
            backup_count = sum(1 for f in backup_dir.rglob("*.dstbak"))
        self.stats_layout.addWidget(_stat_card("Backups", str(backup_count), "#8b5cf6"))
        self.stats_layout.addStretch()

    def refresh(self, _value=None):
        all_names = list_profiles(self.profiles_dir)
        names = [
            name for name in all_names
            if self.search.text().casefold() in name.casefold()
        ]
        self._rebuild_stats(all_names)

        self.table.setRowCount(len(names))
        for row, name in enumerate(names):
            # Name
            item = QTableWidgetItem(f"  {name}")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)

            # Status
            is_active = self.is_profile_active and self.is_profile_active(name)
            status = QTableWidgetItem("● Active" if is_active else "○ Inactive")
            status.setForeground(QColor("#10b981") if is_active else QColor("#6fa8c8"))
            self.table.setItem(row, 1, status)

            # Size
            size_mb = _dir_size_mb(self.profiles_dir / name)
            self.table.setItem(row, 2, QTableWidgetItem(f"{size_mb:.1f} MB"))

            # Storage type
            self.table.setItem(row, 3, QTableWidgetItem("Local"))

        self.table.resizeColumnsToContents()

        if names:
            self.empty_state.hide()
            self.table.show()
        else:
            self.table.hide()
            self.empty_state.setText(
                "No profiles yet. Click '+ New Profile' to get started."
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
        name = item.text().strip()
        if name not in list_profiles(self.profiles_dir):
            self.refresh()
            return
        self.open_profile(name)
        self.accept()

    def create_new_profile(self):
        if self.create_profile is None:
            return
        self.create_profile()
        self.refresh()

    def backup_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Profile", "Select a profile to back up.")
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        name = item.text().strip()
        if name not in list_profiles(self.profiles_dir):
            QMessageBox.warning(self, "Unavailable", "Selected profile no longer exists.")
            self.refresh()
            return
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
            "Encrypted snapshot saved to:\n" + str(destination)
            + "\nKeep the passphrase safe; it cannot be recovered.",
        )

    def restore_new_profile(self):
        path, _filter = QFileDialog.getOpenFileName(
            self, "Select Encrypted Backup",
            str(self.profiles_dir.parent / "backups"),
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
            + "\nWebsite sessions may require signing in again.",
        )

    def open_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.activate(row)
