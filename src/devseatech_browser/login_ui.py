"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign. Existing authentication remains in app.py.
Trial and license activation are deliberately not represented as active
controls until server-side licensing exists.
"""
from __future__ import annotations

import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)


class GalaxyBackground(QWidget):
    """Low-cost animated starfield with reduced-motion compatibility."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tick = 0
        self.setObjectName("galaxy")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(90)

    def advance(self):
        self.tick = (self.tick + 1) % 720
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#030d22"))
        gradient.setColorAt(.53, QColor("#092857"))
        gradient.setColorAt(1, QColor("#02091c"))
        painter.fillRect(self.rect(), gradient)
        for i in range(105):
            x = (i * 163 + 31) % max(1, self.width())
            y = (i * 97 + 17) % max(1, self.height())
            brightness = 75 + int(90 * (1 + math.sin(self.tick / 25 + i)) / 2)
            painter.setPen(QColor(150, 215, 255, brightness))
            painter.drawPoint(x, y)
        # Two low-key shooting stars move behind the controls.
        for i in range(2):
            head_x = (self.tick * (5 + i) + i * 400) % (self.width() + 420) - 210
            head_y = 95 + i * 270 + head_x * .10
            painter.setPen(QPen(QColor(38, 196, 255, 105), 2))
            painter.drawLine(int(head_x - 100), int(head_y - 28),
                             int(head_x), int(head_y))
        painter.end()


def line(text, size=14, color="#d8ecff", bold=False):
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(
        "background: transparent; border: 0; color: %s; font-size: %dpx; font-weight: %s;"
        % (color, size, "700" if bold else "400")
    )
    return label


class BrandedLoginDialog(QDialog):
    """Field keys and return codes retain compatibility with app.py."""

    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSeaTech Universe — " + title)
        self.resize(1180, 740)
        self.setMinimumSize(980, 660)
        self.inputs = {}
        self.setStyleSheet("QDialog { background: #06142b; }")
        background = GalaxyBackground(self)
        shell = QHBoxLayout(background)
        shell.setContentsMargins(36, 36, 36, 36)
        shell.setSpacing(36)

        left = QVBoxLayout()
        left.setSpacing(15)
        left.addWidget(line("◆   DevSeaTech Universe", 30, "#f2f9ff", True))
        left.addWidget(line("SECURE  •  PRIVATE  •  POWERFUL", 12, "#7ecfff"))
        left.addSpacing(65)
        left.addWidget(line("Your secure digital workspace", 26, "#ffffff", True))
        left.addWidget(line(
            "Multi-profile browsing with centralized administration "
            "and flexible licensing.", 15, "#afcce6"
        ))
        left.addSpacing(32)
        for heading, detail in [
            ("◈   Secure Browsing", "Protect browsing data and user access"),
            ("◎   Multi-Profile System", "Isolated cookies, cache and sessions"),
            ("✧   Engine Management", "Multi-version runtime support: planned"),
            ("◉   Proxies & Privacy", "HTTP, HTTPS and SOCKS5: planned"),
            ("◷   Session Time Control", "Administrator-managed sessions"),
        ]:
            left.addWidget(line(heading, 16, "#e6f9ff", True))
            left.addWidget(line(detail, 12, "#97b8d7"))
            left.addSpacing(3)
        left.addStretch()
        contact = QFrame()
        contact.setObjectName("contact")
        contact.setStyleSheet(
            "QFrame#contact { background: rgba(3,22,49,195); "
            "border: 1px solid #1669a7; border-radius: 14px; }"
        )
        contact_layout = QVBoxLayout(contact)
        contact_layout.setContentsMargins(17, 17, 17, 17)
        contact_layout.addWidget(line("CONTACT INFORMATION", 12, "#6dd9ff", True))
        contact_layout.addWidget(line("+8801805839123", 13))
        contact_layout.addWidget(line("devseatech60@gmail.com", 13))
        contact_layout.addWidget(line("www.devseatech.com", 13))
        left.addWidget(contact)
        shell.addLayout(left, 5)

        panel = QFrame()
        panel.setObjectName("accessPanel")
        panel.setStyleSheet("""
            QFrame#accessPanel {
                background-color: rgba(3, 14, 35, 245);
                border: 2px solid #078ad6;
                border-radius: 23px;
            }
            QLineEdit {
                color: #ffffff; background: #102341; padding: 15px;
                border: 1px solid #37638f; border-radius: 10px;
                font-size: 15px;
            }
            QLineEdit:focus { border: 2px solid #15c9ff; }
            QPushButton {
                color: #ffffff; background: #036bcb; border: 1px solid #19bbfa;
                border-radius: 10px; font-size: 15px; font-weight: 700;
                padding: 16px;
            }
            QPushButton:hover { background: #078ff0; }
            QPushButton#recovery {
                background: transparent; color: #76d9ff;
                font-size: 12px; border: none; padding: 8px;
            }
        """)
        right = QVBoxLayout(panel)
        right.setContentsMargins(48, 43, 48, 38)
        right.setSpacing(17)
        heading = line("WELCOME TO", 13, "#7ed7ff", True)
        heading.setAlignment(Qt.AlignCenter)
        right.addWidget(heading)
        brand = line("DevSeaTech Universe", 32, "#ffffff", True)
        brand.setAlignment(Qt.AlignCenter)
        right.addWidget(brand)
        caption = line("SECURE BROWSER ACCESS", 12, "#b8d7ef")
        caption.setAlignment(Qt.AlignCenter)
        right.addWidget(caption)
        right.addSpacing(36)

        for label, secret in fields:
            field_label = line(label.upper(), 12, "#a8c8e6", True)
            right.addWidget(field_label)
            editor = QLineEdit()
            editor.setPlaceholderText("Enter " + label.lower())
            if secret:
                editor.setEchoMode(QLineEdit.Password)
            editor.returnPressed.connect(self.accept)
            self.inputs[label] = editor
            right.addWidget(editor)
        right.addSpacing(13)
        submit = QPushButton(
            "Create Credentials" if title == "First-Time Setup" else "Login to Universe   →"
        )
        submit.clicked.connect(self.accept)
        right.addWidget(submit)
        if title == "Master Login":
            recovery = QPushButton("Forgot both passwords?  Reset preview access")
            recovery.setObjectName("recovery")
            recovery.clicked.connect(lambda: self.done(2))
            right.addWidget(recovery)
        right.addSpacing(25)
        right.addWidget(line("TRIAL LICENSING  •  24h / 72h / custom hours", 12, "#8ebee1"))
        right.addWidget(line(
            "License activation and server recovery will appear after "
            "their secure services are implemented.", 12, "#7192b5"
        ))
        right.addStretch()
        footer = line("Admin Controlled  •  Session Control  •  Profile Isolation", 11, "#80b3df")
        footer.setAlignment(Qt.AlignCenter)
        right.addWidget(footer)
        shell.addWidget(panel, 6)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(background)

    def values(self):
        return {key: editor.text() for key, editor in self.inputs.items()}
