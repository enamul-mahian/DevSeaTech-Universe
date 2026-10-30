"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign. Existing authentication remains in app.py.
Trial and license activation are deliberately not represented as active
controls until server-side licensing exists.
"""
from __future__ import annotations

import math
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (QColor, QLinearGradient, QPainter, QPainterPath,
                          QPen, QPolygonF, QRadialGradient)
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
        """Render a native, resolution-independent cosmic landscape.

        The artwork is drawn with Qt, not a static mockup: the login inputs
        and existing authentication workflow remain fully interactive.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = max(1, self.width()), max(1, self.height())
        sky = QLinearGradient(0, 0, w, h)
        sky.setColorAt(0, QColor("#020818"))
        sky.setColorAt(0.52, QColor("#09295b"))
        sky.setColorAt(1, QColor("#020918"))
        painter.fillRect(self.rect(), sky)

        # Soft galaxy radiance and a distant planetary horizon.
        glow = QRadialGradient(QPointF(w * .63, h * .20), w * .54)
        glow.setColorAt(0, QColor(0, 130, 255, 115))
        glow.setColorAt(.48, QColor(11, 65, 150, 52))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)
        painter.setPen(QPen(QColor(80, 205, 255, 135), 2))
        painter.setBrush(QColor(20, 62, 128, 44))
        painter.drawEllipse(QPointF(w * .90, h * .02),
                            w * .27, h * .34)

        for i in range(185):
            x = (i * 397 + 41) % w
            y = (i * 179 + 29) % h
            brightness = 85 + int(85 * (1 + math.sin(self.tick / 30 + i)) / 2)
            painter.setPen(QColor(170, 224, 255, brightness))
            painter.drawPoint(x, y)

        # Three mountain layers give depth without external image assets.
        for i, (base, top, fill) in enumerate((
            (.82, .49, "#0b2650"),
            (.91, .58, "#071b38"),
            (1.03, .69, "#030d24"),
        )):
            ridge = QPolygonF([QPointF(0, h)])
            for j in range(17):
                x = (j / 16) * w
                peak = h * (top + .10 * (1 + math.sin(j * (2.17 + i) + i)))
                peak += h * .065 * math.sin(j * 4.7 + i)
                ridge.append(QPointF(x, min(h * base, peak)))
            ridge.append(QPointF(w, h))
            ridge.append(QPointF(0, h))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(fill))
            painter.drawPolygon(ridge)
        painter.setPen(QPen(QColor(24, 163, 255, 64), 2))
        painter.drawLine(0, int(h * .85), w, int(h * .89))

        # Shooting stars are decorative only; never cover login controls.
        for i in range(2):
            x = (self.tick * (3 + i) + i * 590) % (w + 380) - 190
            y = h * (.17 + i * .32) + x * .075
            painter.setPen(QPen(QColor(75, 213, 255, 135), 2))
            painter.drawLine(int(x - 115), int(y + 42),
                             int(x), int(y))
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
        self.resize(1280, 790)
        self.setMinimumSize(1050, 690)
        self.inputs = {}
        self.setStyleSheet("QDialog { background: #06142b; }")
        background = GalaxyBackground(self)
        shell = QHBoxLayout(background)
        shell.setContentsMargins(54, 50, 54, 50)
        shell.setSpacing(54)

        left = QVBoxLayout()
        left.setSpacing(13)
        left.addWidget(line("∞   DevSeaTech", 34, "#f2f9ff", True))
        left.addWidget(line("       U N I V E R S E", 17, "#64d7ff", True))
        left.addWidget(line("SECURE  •  PRIVATE  •  POWERFUL", 12, "#7ecfff"))
        left.addSpacing(44)
        left.addWidget(line("Your secure digital workspace", 26, "#ffffff", True))
        left.addWidget(line(
            "Multi-profile browsing with centralized administration "
            "and flexible licensing.", 15, "#afcce6"
        ))
        left.addSpacing(23)
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
            "QFrame#contact { background: rgba(3,22,49,185); "
            "border: 1px solid #3ebdff; border-radius: 18px; }"
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
                background-color: rgba(3, 17, 42, 227);
                border: 2px solid #49cfff;
                border-radius: 28px;
            }
            QLineEdit {
                color: #ffffff; background: #102b50; padding: 15px;
                border: 1px solid #31a9db; border-radius: 10px;
                font-size: 15px;
            }
            QLineEdit:focus { border: 2px solid #15c9ff; }
            QPushButton {
                color: #ffffff; background: #047dd9; border: 1px solid #64e6ff;
                border-radius: 10px; font-size: 15px; font-weight: 700;
                padding: 16px;
            }
            QPushButton:hover { background: #05a7f7; }
            QPushButton:focus { border: 2px solid #d4faff; }
            QPushButton#recovery {
                background: transparent; color: #76d9ff;
                font-size: 12px; border: none; padding: 8px;
            }
        """)
        right = QVBoxLayout(panel)
        right.setContentsMargins(52, 47, 52, 36)
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
        right.addSpacing(48)

        for label, secret in fields:
            field_label = line(label.upper(), 12, "#a8c8e6", True)
            right.addWidget(field_label)
            editor = QLineEdit()
            editor.setPlaceholderText("Enter " + label.lower())
            editor.returnPressed.connect(self.accept)
            self.inputs[label] = editor
            if secret:
                editor.setEchoMode(QLineEdit.Password)
                field_row = QHBoxLayout()
                field_row.setSpacing(8)
                field_row.addWidget(editor, 1)
                visibility = QPushButton("Show")
                visibility.setObjectName("passwordVisibility")
                visibility.setCheckable(True)
                visibility.setAccessibleName("Show " + label.lower())
                visibility.toggled.connect(
                    lambda visible, field=editor, control=visibility, name=label:
                    self._set_password_visibility(field, control, name, visible)
                )
                field_row.addWidget(visibility)
                right.addLayout(field_row)
            else:
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
        right.addSpacing(37)
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

    @staticmethod
    def _set_password_visibility(
        editor: QLineEdit, button: QPushButton, label: str, visible: bool
    ) -> None:
        editor.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        button.setText("Hide" if visible else "Show")
        button.setAccessibleName(
            ("Hide " if visible else "Show ") + label.lower()
        )

    def values(self):
        return {key: editor.text() for key, editor in self.inputs.items()}
