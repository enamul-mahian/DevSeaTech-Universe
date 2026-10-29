"""Branded, English-only DevSeaTech login interface for development previews."""
from __future__ import annotations

import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QFormLayout,
)


class NeonBackdrop(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.ticker = QTimer(self)
        self.ticker.timeout.connect(self.advance)
        self.ticker.start(60)

    def advance(self):
        self.phase = (self.phase + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#06162f"))
        gradient.setColorAt(.48, QColor("#073569"))
        gradient.setColorAt(1, QColor("#d9efff"))
        painter.fillRect(self.rect(), gradient)
        for layer in range(4):
            path = QPainterPath()
            baseline = self.height() * (.55 + layer * .12)
            path.moveTo(0, baseline)
            for x in range(0, self.width() + 15, 15):
                y = baseline + math.sin(x / 110 + self.phase / 95 + layer) * (24 + layer * 6)
                path.lineTo(x, y)
            painter.setPen(QPen(QColor(15, 195, 255, 75 + layer * 25), 2 + layer))
            painter.drawPath(path)
        painter.end()


class BrandedLoginDialog(QDialog):
    """Use the same field labels as the existing credential verification flow."""

    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSeaTech Browser — " + title)
        self.resize(1030, 645)
        self.setMinimumSize(850, 540)
        self.inputs = {}
        backdrop = NeonBackdrop(self)
        root = QHBoxLayout(backdrop)
        root.setContentsMargins(34, 34, 34, 34)
        root.setSpacing(30)

        left = QVBoxLayout()
        left.setSpacing(18)
        brand = QLabel("◈  DevSeaTech")
        brand.setStyleSheet("font-size: 39px; font-weight: 800; color: #e9f8ff;")
        left.addWidget(brand)
        tagline = QLabel("Your Trusted Technology Partner")
        tagline.setStyleSheet("font-size: 15px; color: #b6e9ff;")
        left.addWidget(tagline)
        left.addSpacing(36)
        for line in (
            "✦   Secure Browsing",
            "◈   Multi-Version Engine",
            "●   Multi-Profile System",
            "◎   Proxies & Privacy",
            "▣   Controlled Environment",
        ):
            label = QLabel(line)
            label.setStyleSheet("font-size: 18px; color: #effaff;")
            left.addWidget(label)
        left.addStretch()
        contact = QLabel(
            "CONTACT INFORMATION\n\n"
            "+8801805839123\n"
            "devseatech60@gmail.com\n"
            "www.devseatech.com"
        )
        contact.setStyleSheet(
            "background-color: rgba(1,19,45,185); border: 1px solid #15beef;"
            "border-radius: 17px; padding: 18px; color: white; font-size: 14px;"
        )
        left.addWidget(contact)
        root.addLayout(left, 5)

        panel = QFrame()
        panel.setObjectName("loginPanel")
        panel.setStyleSheet("""
            QFrame#loginPanel { background: rgba(232,246,255,235);
                border: 2px solid #78dcff; border-radius: 24px; }
            QLabel { color: #123b70; background: transparent; }
            QLineEdit { background: #ffffff; color: #09284d; padding: 14px;
                border: 1px solid #75c9ff; border-radius: 10px; font-size: 15px; }
            QLineEdit:focus { border: 2px solid #00b8fa; }
            QPushButton { background: #0966e8; border: 1px solid #37dfff;
                color: white; font-weight: bold; border-radius: 12px; padding: 15px; }
            QPushButton:hover { background: #08a5ee; }
        """)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(35, 45, 35, 35)
        panel_layout.setSpacing(15)
        wordmark = QLabel("DevSeaTech")
        wordmark.setAlignment(Qt.AlignCenter)
        wordmark.setStyleSheet("font-size: 40px; font-weight: 800; color: #0467ba;")
        panel_layout.addWidget(wordmark)
        title_label = QLabel("SECURE BROWSER ACCESS")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 15px; letter-spacing: 2px;")
        panel_layout.addWidget(title_label)
        panel_layout.addSpacing(24)
        form = QFormLayout()
        form.setSpacing(16)
        for label, secret in fields:
            editor = QLineEdit()
            editor.setPlaceholderText(label)
            if secret:
                editor.setEchoMode(QLineEdit.Password)
            form.addRow(label + ":", editor)
            self.inputs[label] = editor
        panel_layout.addLayout(form)
        panel_layout.addSpacing(20)
        submit = QPushButton("Continue to Browser   →")
        submit.clicked.connect(self.accept)
        panel_layout.addWidget(submit)
        if title == "Master Login":
            recovery = QPushButton("Forgot both passwords? Reset this preview")
            recovery.clicked.connect(lambda: self.done(2))
            panel_layout.addWidget(recovery)
        panel_layout.addStretch()
        safety = QLabel("Admin Controlled    •    Session Time Control    •    Secure Profiles")
        safety.setAlignment(Qt.AlignCenter)
        safety.setWordWrap(True)
        safety.setStyleSheet("font-size: 12px; color: #39709d;")
        panel_layout.addWidget(safety)
        root.addWidget(panel, 6)
        holder = QVBoxLayout(self)
        holder.setContentsMargins(0, 0, 0, 0)
        holder.addWidget(backdrop)

    def values(self):
        return {label: widget.text() for label, widget in self.inputs.items()}
