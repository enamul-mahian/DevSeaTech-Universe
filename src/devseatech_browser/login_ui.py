"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign. Existing authentication remains in app.py.
Trial and license activation are deliberately not represented as active
controls until server-side licensing exists.
"""
from __future__ import annotations

import math
import sys
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import (QColor, QLinearGradient, QPainter, QPainterPath,
                          QPen, QPolygonF, QRadialGradient)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QStyle,
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
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.resize(1240, 760)
        self.setMinimumSize(980, 640)
        self.inputs = {}
        self.setStyleSheet("QDialog { background: #06142b; }")
        background = GalaxyBackground(self)
        shell = QHBoxLayout(background)
        shell.setContentsMargins(58, 44, 58, 44)
        shell.setSpacing(60)

        # Content hierarchy: brand + three benefits on the left, a compact
        # interactive authentication card on the right. No filler panels.
        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(line("∞  DevSeaTech", 34, "#f4fbff", True))
        left.addWidget(line("U N I V E R S E", 15, "#55d9ff", True))
        left.addSpacing(7)
        left.addWidget(line("PRIVATE BROWSING  /  YOUR WORKSPACE", 11, "#8ac8e5"))
        left.addStretch(2)
        left.addWidget(line("Your workspace.\nYour control.", 36, "#ffffff", True))
        left.addSpacing(5)
        left.addWidget(line(
            "One secure entrance to your browsing profiles, "
            "sessions and tools.", 16, "#c0d8ed"
        ))
        left.addSpacing(28)
        for heading, detail in [
            ("01   Isolated profiles", "Separate sessions, cookies and storage"),
            ("02   Session control", "Administrator-managed access windows"),
            ("03   Private by design", "Local-first workspace management"),
        ]:
            benefit = QFrame()
            benefit.setObjectName("benefit")
            benefit.setStyleSheet(
                "QFrame#benefit { background: rgba(4, 24, 52, 150); "
                "border-left: 2px solid #39caff; border-radius: 5px; }"
            )
            benefit_layout = QVBoxLayout(benefit)
            benefit_layout.setContentsMargins(18, 12, 12, 12)
            benefit_layout.setSpacing(5)
            benefit_layout.addWidget(line(heading, 15, "#e9f8ff", True))
            benefit_layout.addWidget(line(detail, 12, "#a8c8e4"))
            left.addWidget(benefit)
            left.addSpacing(7)
        left.addStretch(3)
        left.addWidget(line(
            "DEVSEATECH   •   devseatech60@gmail.com   •   +8801805839123",
            11, "#90bddb"
        ))
        shell.addLayout(left, 6)

        # Center a fixed-width form instead of stretching controls to fill
        # the height of the window. This keeps the UI balanced on wide monitors.
        right_column = QVBoxLayout()
        right_column.addStretch(1)
        panel = QFrame()
        panel.setObjectName("accessPanel")
        panel.setMaximumWidth(505)
        panel.setStyleSheet("""
            QFrame#accessPanel {
                background-color: rgba(5, 19, 43, 224);
                border: 1px solid #43b9e9;
                border-radius: 22px;
            }
            QLineEdit {
                color: #ffffff; background: #102a4a;
                padding: 14px; min-height: 27px;
                border: 1px solid #36789c; border-radius: 9px;
                font-size: 15px;
            }
            QLineEdit:focus { border: 2px solid #46dbff; }
            QPushButton {
                color: #ffffff; background: #0879d2;
                border: 1px solid #36baf5;
                border-radius: 9px; font-size: 15px; font-weight: 700;
                padding: 14px;
            }
            QPushButton:hover { background: #069ce6; }
            QPushButton:focus { border: 2px solid #c9f5ff; }
            QPushButton#passwordVisibility {
                background: #10365b; padding: 14px 12px;
            }
            QPushButton#recovery {
                background: transparent; color: #7ad9ff;
                font-size: 12px; font-weight: 400;
                border: none; padding: 7px;
            }
        """)
        right = QVBoxLayout(panel)
        right.setContentsMargins(35, 34, 35, 29)
        right.setSpacing(13)
        eyebrow = line("ACCOUNT ACCESS", 11, "#64dfff", True)
        right.addWidget(eyebrow)
        right.addWidget(line(
            "Welcome back" if title == "Master Login" else title,
            30, "#ffffff", True
        ))
        right.addWidget(line(
            "Enter your master credentials to continue."
            if title == "Master Login"
            else "Securely configure your local credentials.",
            13, "#acc7df"
        ))
        right.addSpacing(22)
        for label, secret in fields:
            right.addWidget(line(label.upper(), 11, "#b6d7ec", True))
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
        right.addSpacing(19)
        submit = QPushButton(
            "Create Credentials" if title == "First-Time Setup"
            else "Unlock Universe  →"
        )
        submit.setObjectName("loginSubmit")
        submit.setMinimumHeight(54)
        submit.clicked.connect(self.accept)
        right.addWidget(submit)
        if title == "Master Login":
            recovery = QPushButton("Reset development-preview access")
            recovery.setObjectName("recovery")
            recovery.clicked.connect(lambda: self.done(2))
            right.addWidget(recovery)
        right.addSpacing(14)
        right.addWidget(line(
            "LOCAL ACCESS  •  ADMIN-PROTECTED SETTINGS", 10, "#759cb8"
        ))
        right_column.addWidget(panel, 0, Qt.AlignHCenter)
        right_column.addStretch(1)
        shell.addLayout(right_column, 5)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(background)

    def showEvent(self, event):
        """Use the native Windows dark caption, preserving OS window controls.

        A frameless Qt dialog would sacrifice native resizing, accessibility
        and snap controls. DWM colors the actual Windows title bar instead.
        """
        super().showEvent(event)
        if sys.platform != "win32":
            return
        try:
            import ctypes

            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            # Windows 10/11 use 20; older Windows 10 builds use 19.
            dwm = ctypes.windll.dwmapi.DwmSetWindowAttribute
            result = dwm(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            if result != 0:
                dwm(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))
            # The border is handled by the OS; keep native drag/resize/snap.
        except (AttributeError, OSError, ValueError):
            # Older platforms retain their system title bar, not a broken UI.
            return

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
