"""Read-only profile dashboard for the desktop development preview.

Profiles are discovered from disk; opening a profile uses the existing Browser
tab API. No profile or credential files are modified by the dashboard.
"""
from __future__ import annotations

from pathlib import Path
from devseatech_browser.profile_listing import list_profiles

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)




class ProfileDashboard(QDialog):
    """First functional iteration of the approved profile management design."""

    def __init__(self, profiles_dir: Path, open_profile, parent=None, create_profile=None):
        super().__init__(parent)
        self.profiles_dir = profiles_dir
        self.open_profile = open_profile
        self.create_profile = create_profile
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
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Profile", "Storage"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(lambda row, _col: self.activate(row))
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        buttons.addWidget(refresh_button)
        if self.create_profile is not None:
            create_button = QPushButton("Create Profile")
            create_button.clicked.connect(self.create_new_profile)
            buttons.addWidget(create_button)
        buttons.addStretch()
        open_button = QPushButton("Open Selected Profile")
        open_button.clicked.connect(self.open_selected)
        buttons.addWidget(open_button)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self, _value=None):
        names = [name for name in list_profiles(self.profiles_dir)
                 if self.search.text().casefold() in name.casefold()]
        self.table.setRowCount(len(names))
        for row, name in enumerate(names):
            item = QTableWidgetItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, QTableWidgetItem("Local profile"))
        self.table.resizeColumnToContents(0)

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

    def open_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.activate(row)
