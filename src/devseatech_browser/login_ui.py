"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign. Existing authentication remains in app.py.
Trial and license activation are deliberately not represented as active
controls until server-side licensing exists.
"""
from __future__ import annotations

import math
import random
import sys
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (QColor, QLinearGradient, QPainter, QPainterPath,
                          QPen, QPolygonF, QRadialGradient, QFont,
                          QConicalGradient)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QStyle, QGraphicsDropShadowEffect,
    QSizePolicy,
)


# ─── Colour palette ─────────────────────────────────────────────────
_DEEP = "#020a1a"
_MID  = "#0a1e3d"
_ACCENT = "#00d4ff"
_ACCENT_DIM = "#0891b2"
_GLOW = "#00b4d8"
_TEXT = "#e8f4ff"
_TEXT_DIM = "#8cb4d0"
_CARD_BG = "rgba(6, 18, 42, 235)"
_CARD_BORDER = "rgba(0, 180, 216, 0.35)"
_INPUT_BG = "#0c2240"
_INPUT_BORDER = "#1a4a6e"
_BTN_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0077cc, stop:1 #00aadd)"
_BTN_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0088dd, stop:1 #00bbee)"


class _Star:
    """Pre-computed star position with twinkle phase."""
    __slots__ = ('x_frac', 'y_frac', 'size', 'phase', 'base_alpha')

    def __init__(self):
        self.x_frac = random.random()
        self.y_frac = random.random()
        self.size = random.choice([1, 1, 1, 2, 2, 3])
        self.phase = random.uniform(0, math.tau)
        self.base_alpha = random.randint(60, 200)


class CosmicBackground(QWidget):
    """Smooth animated cosmic background with nebula, stars, and aurora."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tick = 0
        self.setObjectName("cosmic")
        self._stars = [_Star() for _ in range(220)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)
        self.timer.start(50)

    def _advance(self):
        self.tick = (self.tick + 1) % 3600
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = max(1, self.width()), max(1, self.height())
        t = self.tick

        # ── Deep space gradient ──
        sky = QLinearGradient(0, 0, w * 0.3, h)
        sky.setColorAt(0.0, QColor("#010714"))
        sky.setColorAt(0.3, QColor("#071e3a"))
        sky.setColorAt(0.6, QColor("#0a1428"))
        sky.setColorAt(1.0, QColor("#020810"))
        p.fillRect(self.rect(), sky)

        # ── Primary nebula — upper right ──
        neb1 = QRadialGradient(QPointF(w * 0.72, h * 0.18), w * 0.48)
        neb1.setColorAt(0.0, QColor(0, 120, 220, 70))
        neb1.setColorAt(0.3, QColor(0, 80, 180, 35))
        neb1.setColorAt(0.6, QColor(10, 40, 100, 15))
        neb1.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), neb1)

        # ── Secondary nebula — lower left (subtle purple) ──
        neb2 = QRadialGradient(QPointF(w * 0.15, h * 0.75), w * 0.35)
        neb2.setColorAt(0.0, QColor(60, 20, 120, 30))
        neb2.setColorAt(0.5, QColor(30, 10, 80, 12))
        neb2.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), neb2)

        # ── Distant planet with subtle ring ──
        planet_cx, planet_cy = w * 0.88, h * 0.08
        planet_r = min(w, h) * 0.09
        planet_grad = QRadialGradient(
            QPointF(planet_cx - planet_r * 0.3, planet_cy - planet_r * 0.3),
            planet_r * 1.2
        )
        planet_grad.setColorAt(0.0, QColor(40, 100, 160, 80))
        planet_grad.setColorAt(0.6, QColor(15, 50, 100, 50))
        planet_grad.setColorAt(1.0, QColor(5, 15, 40, 20))
        p.setPen(QPen(QColor(60, 160, 220, 40), 1))
        p.setBrush(planet_grad)
        p.drawEllipse(QPointF(planet_cx, planet_cy), planet_r, planet_r)
        # Thin ring
        p.setPen(QPen(QColor(80, 180, 240, 35), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(planet_cx, planet_cy),
                      planet_r * 1.6, planet_r * 0.35)

        # ── Stars with twinkle (all drawn as tiny ellipses for DPI safety) ──
        for s in self._stars:
            x = s.x_frac * w
            y = s.y_frac * h
            twinkle = 0.5 + 0.5 * math.sin(t * 0.06 + s.phase)
            alpha = int(s.base_alpha * (0.4 + 0.6 * twinkle))
            r = max(0.6, s.size * 0.5)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(200, 230, 255, alpha))
            p.drawEllipse(QPointF(x, y), r, r)

        # ── Horizon glow line ──
        horizon_y = h * 0.82
        glow_line = QLinearGradient(0, horizon_y - 30, 0, horizon_y + 30)
        glow_line.setColorAt(0.0, QColor(0, 0, 0, 0))
        glow_line.setColorAt(0.5, QColor(0, 140, 210, 25))
        glow_line.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, horizon_y - 30, w, 60), glow_line)

        # ── Mountain silhouettes (3 layers) ──
        mountains = [
            (0.78, 0.52, QColor(8, 28, 55, 220), 2.3),
            (0.88, 0.62, QColor(5, 18, 38, 240), 1.7),
            (1.02, 0.72, QColor(3, 10, 24, 255), 3.1),
        ]
        for base_y, peak_y, color, freq_offset in mountains:
            poly = QPolygonF([QPointF(0, h)])
            segments = 24
            for j in range(segments + 1):
                x = (j / segments) * w
                peak = h * (peak_y
                            + 0.07 * math.sin(j * 0.8 + freq_offset)
                            + 0.04 * math.sin(j * 2.1 + freq_offset * 1.5)
                            + 0.02 * math.sin(j * 4.3 + freq_offset * 0.7))
                y = min(h * base_y, peak)
                poly.append(QPointF(x, y))
            poly.append(QPointF(w, h))
            poly.append(QPointF(0, h))
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawPolygon(poly)

        # ── Shooting stars ──
        for i in range(3):
            speed = 2.5 + i * 1.2
            length = 80 + i * 40
            sx = (t * speed + i * 800) % (w + 600) - 300
            sy = h * (0.10 + i * 0.22) + sx * 0.06
            alpha = max(0, min(160, 160 - abs(sx - w * 0.5) // 3))
            if alpha > 10:
                trail = QLinearGradient(QPointF(sx, sy),
                                        QPointF(sx - length, sy + length * 0.3))
                trail.setColorAt(0.0, QColor(180, 240, 255, alpha))
                trail.setColorAt(1.0, QColor(180, 240, 255, 0))
                p.setPen(QPen(trail, 1.5))
                p.drawLine(QPointF(sx, sy),
                           QPointF(sx - length, sy + length * 0.3))

        # ── Aurora shimmer at horizon ──
        aurora_phase = t * 0.02
        for i in range(5):
            ax = w * (0.1 + i * 0.2)
            ay = h * 0.76
            wave = math.sin(aurora_phase + i * 1.3) * h * 0.03
            aurora_grad = QRadialGradient(QPointF(ax, ay + wave), w * 0.12)
            aurora_color = QColor(0, 200, 255, int(15 + 10 * math.sin(aurora_phase + i)))
            aurora_grad.setColorAt(0.0, aurora_color)
            aurora_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(self.rect(), aurora_grad)

        p.end()


def _label(text, size=14, color=_TEXT, bold=False, letter_spacing=0):
    """Create a styled label with optional letter spacing."""
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    font_weight = "600" if bold else "400"
    style = (f"background: transparent; border: 0; color: {color}; "
             f"font-size: {size}px; font-weight: {font_weight};")
    # NOTE: letter-spacing via CSS causes rendering artifacts on Windows Qt.
    # Use QFont.setLetterSpacing() instead when spacing is needed.
    lbl.setStyleSheet(style)
    if letter_spacing > 0:
        font = lbl.font()
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)
        lbl.setFont(font)
    return lbl


def _separator():
    """Thin horizontal accent line."""
    sep = QFrame()
    sep.setFixedHeight(1)
    sep.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        "stop:0 transparent, stop:0.2 #0891b2, stop:0.8 #0891b2, "
        "stop:1 transparent);"
    )
    return sep


class BrandedLoginDialog(QDialog):
    """Field keys and return codes retain compatibility with app.py."""

    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSeaTech Universe — " + title)
        self.setWindowIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon))
        self.resize(1280, 780)
        self.setMinimumSize(960, 620)
        self.inputs: dict[str, QLineEdit] = {}

        self.setStyleSheet("QDialog { background: #020a1a; }")

        bg = CosmicBackground(self)
        shell = QHBoxLayout(bg)
        shell.setContentsMargins(64, 48, 56, 36)
        shell.setSpacing(48)

        # ═══════════════════════════════════════════════════
        #  LEFT SIDE — Brand, tagline, feature highlights
        # ═══════════════════════════════════════════════════
        left = QVBoxLayout()
        left.setSpacing(8)

        # Brand mark
        brand = _label("∞  DevSeaTech", 38, "#ffffff", True)
        left.addWidget(brand)

        universe_tag = _label("U N I V E R S E", 13, _ACCENT, True, 4)
        left.addWidget(universe_tag)

        left.addSpacing(4)
        breadcrumb = _label("PRIVATE BROWSING  /  YOUR WORKSPACE", 10,
                            _TEXT_DIM, letter_spacing=2)
        left.addWidget(breadcrumb)

        left.addStretch(3)

        # Hero text
        hero = _label("Your workspace.\nYour control.", 40, "#ffffff", True)
        hero.setStyleSheet(hero.styleSheet().replace("}", "line-height: 120%; }"))
        left.addWidget(hero)
        left.addSpacing(6)

        subtitle = _label(
            "One secure entrance to your browsing profiles,\n"
            "sessions, and tools.",
            16, "#b0ccdf"
        )
        left.addWidget(subtitle)

        left.addSpacing(24)
        left.addWidget(_separator())
        left.addSpacing(16)

        # Feature highlights with numbered badges
        features = [
            ("01", "Isolated profiles",
             "Separate sessions, cookies and storage"),
            ("02", "Session control",
             "Administrator-managed access windows"),
            ("03", "Private by design",
             "Local-first workspace management"),
        ]
        for num, heading, detail in features:
            row = QHBoxLayout()
            row.setSpacing(14)
            row.setContentsMargins(0, 0, 0, 0)

            # Number badge
            badge = QLabel(num)
            badge.setFixedSize(32, 32)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                f"background: rgba(0, 180, 216, 0.12); "
                f"border: 1px solid rgba(0, 180, 216, 0.3); "
                f"border-radius: 6px; color: {_ACCENT}; "
                f"font-size: 12px; font-weight: 700;"
            )
            row.addWidget(badge, 0, Qt.AlignTop)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            text_col.addWidget(_label(heading, 14, "#e0f0ff", True))
            text_col.addWidget(_label(detail, 12, _TEXT_DIM))
            row.addLayout(text_col, 1)

            left.addLayout(row)
            left.addSpacing(10)

        left.addStretch(4)

        # Footer
        left.addWidget(_separator())
        left.addSpacing(8)
        footer = _label(
            "DEVSEATECH   •   devseatech60@gmail.com   •   +8801805839123",
            10, "#607890", letter_spacing=1
        )
        left.addWidget(footer)

        shell.addLayout(left, 55)

        # ═══════════════════════════════════════════════════
        #  RIGHT SIDE — Auth card (vertically centred)
        # ═══════════════════════════════════════════════════
        right_col = QVBoxLayout()
        right_col.addStretch(1)

        card = QFrame()
        card.setObjectName("authCard")
        card.setMaximumWidth(440)
        card.setMinimumWidth(360)
        card.setStyleSheet(f"""
            QFrame#authCard {{
                background-color: {_CARD_BG};
                border: 1px solid {_CARD_BORDER};
                border-radius: 20px;
            }}
            QLineEdit {{
                color: #ffffff;
                background: {_INPUT_BG};
                padding: 13px 16px;
                min-height: 24px;
                border: 1px solid {_INPUT_BORDER};
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #0077cc;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {_ACCENT};
            }}
            QLineEdit::placeholder {{
                color: #4a6a84;
            }}
            QPushButton#loginSubmit {{
                color: #ffffff;
                background: {_BTN_PRIMARY};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                padding: 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton#loginSubmit:hover {{
                background: {_BTN_HOVER};
            }}
            QPushButton#loginSubmit:pressed {{
                background: #006bb3;
            }}
            QPushButton#loginSubmit:focus {{
                outline: 2px solid {_ACCENT};
                outline-offset: 2px;
            }}
            QPushButton#passwordVisibility {{
                background: rgba(0, 180, 216, 0.08);
                border: 1px solid rgba(0, 180, 216, 0.25);
                border-radius: 10px;
                color: {_ACCENT};
                font-size: 12px;
                font-weight: 600;
                padding: 13px 14px;
                min-width: 48px;
            }}
            QPushButton#passwordVisibility:hover {{
                background: rgba(0, 180, 216, 0.15);
            }}
            QPushButton#recovery {{
                background: transparent;
                color: {_ACCENT_DIM};
                font-size: 12px;
                font-weight: 400;
                border: none;
                padding: 6px;
            }}
            QPushButton#recovery:hover {{
                color: {_ACCENT};
            }}
        """)

        # Glow effect behind card
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(60)
        glow_effect.setColor(QColor(0, 140, 200, 30))
        glow_effect.setOffset(0, 4)
        card.setGraphicsEffect(glow_effect)

        form = QVBoxLayout(card)
        form.setContentsMargins(36, 32, 36, 28)
        form.setSpacing(10)

        # Card header — eyebrow with shield character
        eyebrow = _label("⬡  SECURE ACCESS", 10, _ACCENT, True, 3)
        form.addWidget(eyebrow)

        form.addSpacing(6)

        # Title
        is_login = title == "Master Login"
        card_title = _label(
            "Welcome back" if is_login else title,
            26, "#ffffff", True
        )
        form.addWidget(card_title)

        card_sub = _label(
            "Enter your master credentials to continue."
            if is_login
            else "Set up your local credentials to get started.",
            13, "#8cafc8"
        )
        form.addWidget(card_sub)

        form.addSpacing(18)

        # ── Input fields ──
        for label_text, secret in fields:
            field_label = _label(label_text.upper(), 11, _TEXT_DIM, True, 1)
            form.addWidget(field_label)
            form.addSpacing(4)

            editor = QLineEdit()
            editor.setPlaceholderText("Enter " + label_text.lower() + "...")
            editor.returnPressed.connect(self.accept)
            self.inputs[label_text] = editor

            if secret:
                editor.setEchoMode(QLineEdit.Password)
                field_row = QHBoxLayout()
                field_row.setSpacing(8)
                field_row.addWidget(editor, 1)

                vis_btn = QPushButton("Show")
                vis_btn.setObjectName("passwordVisibility")
                vis_btn.setCheckable(True)
                vis_btn.setCursor(Qt.PointingHandCursor)
                vis_btn.setAccessibleName("Show " + label_text.lower())
                vis_btn.toggled.connect(
                    lambda visible, f=editor, b=vis_btn, n=label_text:
                    self._set_password_visibility(f, b, n, visible)
                )
                field_row.addWidget(vis_btn)
                form.addLayout(field_row)
            else:
                form.addWidget(editor)

            form.addSpacing(8)

        form.addSpacing(12)

        # Submit button
        submit_text = ("Create Credentials" if title == "First-Time Setup"
                       else "Unlock Universe  →")
        submit = QPushButton(submit_text)
        submit.setObjectName("loginSubmit")
        submit.setMinimumHeight(50)
        submit.setCursor(Qt.PointingHandCursor)
        submit.clicked.connect(self.accept)
        form.addWidget(submit)

        # Recovery link
        if is_login:
            form.addSpacing(4)
            recovery = QPushButton("Reset development-preview access")
            recovery.setObjectName("recovery")
            recovery.setCursor(Qt.PointingHandCursor)
            recovery.clicked.connect(lambda: self.done(2))
            form.addWidget(recovery, 0, Qt.AlignCenter)

        form.addSpacing(12)

        # Card footer
        card_footer_sep = QFrame()
        card_footer_sep.setFixedHeight(1)
        card_footer_sep.setStyleSheet(
            "background: rgba(0, 180, 216, 0.15);")
        form.addWidget(card_footer_sep)
        form.addSpacing(8)
        form.addWidget(
            _label("LOCAL ACCESS  •  ADMIN-PROTECTED", 9,
                   "#506878"),
            0, Qt.AlignCenter
        )

        right_col.addWidget(card, 0, Qt.AlignHCenter)
        right_col.addStretch(1)
        shell.addLayout(right_col, 45)

        # Final layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(bg)

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
            # Windows 10/11 use attribute 20; older builds use 19.
            dwm = ctypes.windll.dwmapi.DwmSetWindowAttribute
            result = dwm(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            if result != 0:
                dwm(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))
        except (AttributeError, OSError, ValueError):
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
