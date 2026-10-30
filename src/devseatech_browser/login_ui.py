"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign. Existing authentication remains in app.py.
Trial and license activation are deliberately not represented as active
controls until server-side licensing exists.
"""
from __future__ import annotations

import math
import random
import sys
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QSize
from PySide6.QtGui import (QColor, QLinearGradient, QPainter, QPainterPath,
                          QPen, QPolygonF, QRadialGradient, QFont, QBrush,
                          QIcon, QPixmap)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QStyle, QGraphicsDropShadowEffect,
    QSizePolicy, QApplication,
)


# ─── Colour palette ─────────────────────────────────────────────────
_DEEP = "#020a1a"
_ACCENT = "#00d4ff"
_ACCENT_GLOW = "#00b8e6"
_TEXT = "#e8f4ff"
_TEXT_DIM = "#7da4be"
_CARD_BG = "rgba(4, 14, 36, 230)"
_INPUT_BG = "#081c38"
_INPUT_BORDER = "#164060"


class _Star:
    __slots__ = ('x_frac', 'y_frac', 'size', 'phase', 'base_alpha')
    def __init__(self):
        self.x_frac = random.random()
        self.y_frac = random.random() * 0.7  # stars only in upper 70%
        self.size = random.choice([0.6, 0.8, 1.0, 1.2, 1.5, 2.0])
        self.phase = random.uniform(0, math.tau)
        self.base_alpha = random.randint(80, 220)


class CosmicBackground(QWidget):
    """Rich animated cosmic background matching the premium reference."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tick = 0
        self._stars = [_Star() for _ in range(280)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)
        self.timer.start(50)

    def _advance(self):
        self.tick = (self.tick + 1) % 7200
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = max(1, self.width()), max(1, self.height())
        t = self.tick

        # ── Deep space gradient ──
        sky = QLinearGradient(0, 0, w * 0.4, h)
        sky.setColorAt(0.0, QColor("#010510"))
        sky.setColorAt(0.25, QColor("#041228"))
        sky.setColorAt(0.5, QColor("#071a3a"))
        sky.setColorAt(0.75, QColor("#051530"))
        sky.setColorAt(1.0, QColor("#020812"))
        p.fillRect(self.rect(), sky)

        # ── Large nebula — upper center-right ──
        neb = QRadialGradient(QPointF(w * 0.65, h * 0.15), w * 0.55)
        neb.setColorAt(0.0, QColor(0, 80, 180, 55))
        neb.setColorAt(0.25, QColor(0, 50, 140, 35))
        neb.setColorAt(0.5, QColor(5, 30, 90, 18))
        neb.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), neb)

        # ── Secondary nebula — upper left (deep blue) ──
        neb2 = QRadialGradient(QPointF(w * 0.2, h * 0.1), w * 0.35)
        neb2.setColorAt(0.0, QColor(10, 40, 120, 40))
        neb2.setColorAt(0.5, QColor(5, 20, 70, 15))
        neb2.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), neb2)

        # ── Large planet (right side) ──
        planet_cx = w * 0.78
        planet_cy = h * 0.22
        planet_r = min(w, h) * 0.22
        # Planet body
        pg = QRadialGradient(
            QPointF(planet_cx - planet_r * 0.25, planet_cy - planet_r * 0.2),
            planet_r * 1.3)
        pg.setColorAt(0.0, QColor(30, 90, 160, 90))
        pg.setColorAt(0.4, QColor(15, 55, 120, 70))
        pg.setColorAt(0.7, QColor(8, 30, 80, 50))
        pg.setColorAt(1.0, QColor(3, 10, 30, 20))
        p.setPen(Qt.NoPen)
        p.setBrush(pg)
        p.drawEllipse(QPointF(planet_cx, planet_cy), planet_r, planet_r)
        # Planet edge glow
        edge_glow = QRadialGradient(QPointF(planet_cx, planet_cy), planet_r * 1.15)
        edge_glow.setColorAt(0.85, QColor(0, 0, 0, 0))
        edge_glow.setColorAt(0.92, QColor(0, 160, 255, 40))
        edge_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(edge_glow)
        p.drawEllipse(QPointF(planet_cx, planet_cy),
                      planet_r * 1.15, planet_r * 1.15)
        # Atmospheric ring
        p.setPen(QPen(QColor(60, 180, 240, 30), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(planet_cx, planet_cy),
                      planet_r * 1.8, planet_r * 0.4)

        # ── Stars ──
        for s in self._stars:
            x = s.x_frac * w
            y = s.y_frac * h
            twinkle = 0.5 + 0.5 * math.sin(t * 0.05 + s.phase)
            alpha = int(s.base_alpha * (0.3 + 0.7 * twinkle))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(200, 230, 255, alpha))
            p.drawEllipse(QPointF(x, y), s.size, s.size)

        # ── Mountain silhouettes (4 layers for depth) ──
        mtn_data = [
            (0.72, 0.46, QColor(12, 35, 70, 200), 1.9, 0.09),
            (0.80, 0.54, QColor(8, 25, 55, 220), 2.5, 0.08),
            (0.88, 0.63, QColor(5, 18, 40, 240), 3.1, 0.07),
            (1.01, 0.74, QColor(3, 10, 25, 255), 1.3, 0.06),
        ]
        for base_y, peak_y, color, freq, amp in mtn_data:
            poly = QPolygonF([QPointF(0, h)])
            segs = 32
            for j in range(segs + 1):
                x = (j / segs) * w
                y_val = h * (peak_y
                             + amp * math.sin(j * 0.6 + freq)
                             + amp * 0.6 * math.sin(j * 1.4 + freq * 1.7)
                             + amp * 0.3 * math.sin(j * 3.2 + freq * 0.5))
                poly.append(QPointF(x, min(h * base_y, y_val)))
            poly.append(QPointF(w, h))
            poly.append(QPointF(0, h))
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawPolygon(poly)

        # ── Water/lake reflection at bottom ──
        water_y = h * 0.82
        water = QLinearGradient(0, water_y, 0, h)
        water.setColorAt(0.0, QColor(5, 25, 60, 100))
        water.setColorAt(0.3, QColor(3, 18, 45, 140))
        water.setColorAt(1.0, QColor(2, 10, 25, 180))
        p.fillRect(QRectF(0, water_y, w, h - water_y), water)
        # Reflection shimmer lines
        for i in range(8):
            ry = water_y + 10 + i * ((h - water_y - 10) / 8)
            rx = w * (0.3 + 0.05 * math.sin(t * 0.03 + i * 0.7))
            rw = w * (0.1 + 0.05 * math.sin(t * 0.02 + i * 1.3))
            alpha = int(20 + 15 * math.sin(t * 0.04 + i))
            p.setPen(QPen(QColor(0, 180, 255, alpha), 1))
            p.drawLine(QPointF(rx, ry), QPointF(rx + rw, ry))

        # ── Horizon glow ──
        hg = QLinearGradient(0, water_y - 20, 0, water_y + 20)
        hg.setColorAt(0.0, QColor(0, 0, 0, 0))
        hg.setColorAt(0.5, QColor(0, 150, 220, 35))
        hg.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, water_y - 20, w, 40), hg)

        # ── Shooting stars ──
        for i in range(3):
            speed = 2.0 + i * 1.5
            length = 100 + i * 30
            sx = (t * speed + i * 900) % (w + 600) - 300
            sy = h * (0.06 + i * 0.15) + sx * 0.05
            alpha = max(0, min(140, 140 - abs(sx - w * 0.5) // 4))
            if alpha > 8:
                trail_grad = QLinearGradient(
                    QPointF(sx, sy),
                    QPointF(sx - length, sy + length * 0.25))
                trail_grad.setColorAt(0.0, QColor(200, 240, 255, alpha))
                trail_grad.setColorAt(1.0, QColor(200, 240, 255, 0))
                p.setPen(QPen(trail_grad, 1.5))
                p.drawLine(QPointF(sx, sy),
                           QPointF(sx - length, sy + length * 0.25))

        p.end()


def _text(text, size=14, color=_TEXT, bold=False):
    """Create a styled label."""
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    weight = "700" if bold else "400"
    lbl.setStyleSheet(
        f"background: transparent; border: 0; color: {color}; "
        f"font-size: {size}px; font-weight: {weight};")
    return lbl


def _icon_circle(icon_char: str, size: int = 44):
    """Create a circle badge with an icon character."""
    badge = QLabel(icon_char)
    badge.setFixedSize(size, size)
    badge.setAlignment(Qt.AlignCenter)
    badge.setStyleSheet(
        f"background: rgba(0, 180, 230, 0.10); "
        f"border: 1.5px solid rgba(0, 180, 230, 0.35); "
        f"border-radius: {size // 2}px; "
        f"color: {_ACCENT}; font-size: {size // 2 - 2}px;")
    return badge


class _NeonFrame(QFrame):
    """Frame with painted neon glow border."""

    def __init__(self, glow_color=QColor(0, 180, 255, 80), parent=None):
        super().__init__(parent)
        self._glow = glow_color

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = 18
        rect = QRectF(self.rect()).adjusted(3, 3, -3, -3)
        # Outer glow layers
        for i, (spread, alpha) in enumerate([
            (6, 18), (4, 30), (2, 50), (1, 80)
        ]):
            c = QColor(self._glow)
            c.setAlpha(alpha)
            p.setPen(QPen(c, spread))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect, r, r)
        # Bright inner border
        c = QColor(self._glow)
        c.setAlpha(120)
        p.setPen(QPen(c, 1.5))
        p.drawRoundedRect(rect, r, r)
        p.end()


class BrandedLoginDialog(QDialog):
    """Field keys and return codes retain compatibility with app.py."""

    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSeaTech Universe — " + title)
        self.setWindowIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon))
        self.resize(1340, 820)
        self.setMinimumSize(1020, 660)
        self.inputs: dict[str, QLineEdit] = {}
        self.setStyleSheet("QDialog { background: #010714; }")

        bg = CosmicBackground(self)
        shell = QHBoxLayout(bg)
        shell.setContentsMargins(52, 40, 44, 32)
        shell.setSpacing(40)

        is_login = title == "Master Login"
        is_setup = title == "First-Time Setup"

        # ═══════════════════════════════════════════════════
        #  LEFT SIDE — Brand, tagline, features, contact
        # ═══════════════════════════════════════════════════
        left = QVBoxLayout()
        left.setSpacing(6)

        # ── Logo area ──
        logo_text = QLabel("DevSeaTech")
        logo_font = QFont()
        logo_font.setPixelSize(42)
        logo_font.setBold(True)
        logo_text.setFont(logo_font)
        logo_text.setStyleSheet(
            "background: transparent; border: 0; color: #ffffff;")
        left.addWidget(logo_text)

        universe_lbl = _text("Universe", 22, _ACCENT, True)
        left.addWidget(universe_lbl)

        left.addSpacing(16)

        # Tagline
        left.addWidget(_text("Your secure digital workspace", 20,
                             "#ffffff", True))
        left.addSpacing(4)
        left.addWidget(_text(
            "Multi-profile browsing with centralized administration\n"
            "and flexible licensing.", 13, _TEXT_DIM))

        left.addSpacing(20)

        # ── Feature list with circle icons ──
        features = [
            ("🛡", "Secure Browsing",
             "Protect browsing data and user access."),
            ("👥", "Multi-Profile System",
             "Isolated cookies, cache and sessions."),
            ("⚙", "Engine Management",
             "Multi-version runtime support: planned."),
            ("🌐", "Proxies & Privacy",
             "HTTP, HTTPS and SOCKS5: planned."),
            ("⏱", "Session Time Control",
             "Administrator-managed sessions."),
        ]
        for icon_ch, heading, detail in features:
            row = QHBoxLayout()
            row.setSpacing(14)
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(_icon_circle(icon_ch, 42), 0, Qt.AlignTop)
            col = QVBoxLayout()
            col.setSpacing(1)
            col.addWidget(_text(heading, 14, "#e4f0ff", True))
            col.addWidget(_text(detail, 11, _TEXT_DIM))
            row.addLayout(col, 1)
            left.addLayout(row)
            left.addSpacing(6)

        left.addStretch(1)

        # ── Contact info panel ──
        contact = _NeonFrame(QColor(0, 160, 220, 50))
        contact.setStyleSheet(
            "QFrame { background: rgba(4, 16, 40, 200); "
            "border-radius: 14px; }")
        contact_layout = QVBoxLayout(contact)
        contact_layout.setContentsMargins(20, 14, 20, 14)
        contact_layout.setSpacing(5)
        contact_layout.addWidget(_text("CONTACT INFORMATION", 10,
                                       _ACCENT, True))
        contact_layout.addSpacing(4)
        for icon, info in [
            ("✉", "devseatech60@gmail.com"),
            ("☎", "+8801805839123"),
            ("⊕", "www.devseatech.com"),
        ]:
            info_row = QHBoxLayout()
            info_row.setSpacing(10)
            icon_lbl = _text(icon, 13, _ACCENT)
            icon_lbl.setFixedWidth(20)
            info_row.addWidget(icon_lbl)
            info_row.addWidget(_text(info, 12, "#c0d8ed"))
            info_row.addStretch()
            contact_layout.addLayout(info_row)
        left.addWidget(contact)

        shell.addLayout(left, 48)

        # ═══════════════════════════════════════════════════
        #  RIGHT SIDE — Auth card with neon glow
        # ═══════════════════════════════════════════════════
        right_col = QVBoxLayout()
        right_col.addStretch(1)

        card = _NeonFrame(QColor(0, 180, 255, 90))
        card.setObjectName("authCard")
        card.setMaximumWidth(480)
        card.setMinimumWidth(380)
        card.setStyleSheet(f"""
            QFrame#authCard {{
                background-color: {_CARD_BG};
                border-radius: 18px;
            }}
            QLineEdit {{
                color: #ffffff;
                background: {_INPUT_BG};
                padding: 13px 16px 13px 14px;
                min-height: 22px;
                border: 1px solid {_INPUT_BORDER};
                border-radius: 10px;
                font-size: 14px;
                selection-background-color: #0077cc;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {_ACCENT};
            }}
            QLineEdit::placeholder {{
                color: #3d6080;
            }}
            QPushButton#loginSubmit {{
                color: #ffffff;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0088cc, stop:0.5 #00bbdd, stop:1 #00ccee);
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                padding: 15px;
            }}
            QPushButton#loginSubmit:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0099dd, stop:0.5 #00ccee, stop:1 #00ddff);
            }}
            QPushButton#loginSubmit:pressed {{
                background: #0077bb;
            }}
            QPushButton#passwordVisibility {{
                background: rgba(0, 160, 220, 0.08);
                border: 1px solid rgba(0, 160, 220, 0.30);
                border-radius: 10px;
                color: {_ACCENT};
                font-size: 13px;
                font-weight: 600;
                padding: 13px 16px;
            }}
            QPushButton#passwordVisibility:hover {{
                background: rgba(0, 160, 220, 0.18);
            }}
            QPushButton#linkBtn {{
                background: transparent;
                color: {_ACCENT};
                font-size: 12px;
                border: none;
                padding: 4px;
                text-decoration: underline;
            }}
            QPushButton#linkBtn:hover {{
                color: #40e8ff;
            }}
        """)

        # Glow shadow
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(80)
        glow.setColor(QColor(0, 140, 220, 40))
        glow.setOffset(0, 0)
        card.setGraphicsEffect(glow)

        form = QVBoxLayout(card)
        form.setContentsMargins(40, 36, 40, 28)
        form.setSpacing(8)

        # Card header
        form.addWidget(_text("WELCOME TO", 11, _TEXT_DIM, True))
        form.addSpacing(2)

        card_title = QLabel("DevSeaTech Universe")
        title_font = QFont()
        title_font.setPixelSize(30)
        title_font.setBold(True)
        card_title.setFont(title_font)
        card_title.setStyleSheet(
            "background: transparent; border: 0; color: #ffffff;")
        card_title.setAlignment(Qt.AlignCenter)
        form.addWidget(card_title)

        form.addSpacing(2)
        subtitle = _text("SECURE BROWSER ACCESS", 11, _TEXT_DIM, True)
        subtitle.setAlignment(Qt.AlignCenter)
        form.addWidget(subtitle)

        form.addSpacing(20)

        # ── Input fields ──
        for label_text, secret in fields:
            form.addWidget(_text(label_text.upper(), 11, "#a0bcd0", True))
            form.addSpacing(4)

            editor = QLineEdit()
            editor.setPlaceholderText("Enter " + label_text.lower())
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
                    lambda vis, f=editor, b=vis_btn, n=label_text:
                    self._set_password_visibility(f, b, n, vis))
                field_row.addWidget(vis_btn)
                form.addLayout(field_row)
            else:
                form.addWidget(editor)
            form.addSpacing(6)

        form.addSpacing(10)

        # Submit
        submit_label = ("Create Credentials" if is_setup
                        else "Login to Universe  →")
        submit = QPushButton(submit_label)
        submit.setObjectName("loginSubmit")
        submit.setMinimumHeight(52)
        submit.setCursor(Qt.PointingHandCursor)
        submit.clicked.connect(self.accept)
        form.addWidget(submit)

        # Links row
        if is_login:
            form.addSpacing(6)
            links_row = QHBoxLayout()
            links_row.addStretch()

            recovery = QPushButton("Reset preview access")
            recovery.setObjectName("linkBtn")
            recovery.setCursor(Qt.PointingHandCursor)
            recovery.clicked.connect(lambda: self.done(2))
            links_row.addWidget(recovery)

            links_row.addStretch()
            form.addLayout(links_row)

        # ── Trial licensing info (informational only) ──
        form.addSpacing(12)
        trial_sep = QFrame()
        trial_sep.setFixedHeight(1)
        trial_sep.setStyleSheet("background: rgba(0, 160, 220, 0.15);")
        form.addWidget(trial_sep)
        form.addSpacing(10)

        trial_row = QHBoxLayout()
        trial_row.setSpacing(12)
        info_icon = _text("ⓘ", 16, _ACCENT)
        info_icon.setFixedWidth(22)
        trial_row.addWidget(info_icon, 0, Qt.AlignTop)
        trial_col = QVBoxLayout()
        trial_col.setSpacing(3)
        trial_col.addWidget(_text(
            "TRIAL LICENSING  •  24h / 72h / custom hours",
            11, "#c0d8ed", True))
        trial_col.addWidget(_text(
            "License activation and server recovery will appear\n"
            "after their secure services are implemented.",
            10, "#607890"))
        trial_row.addLayout(trial_col, 1)
        form.addLayout(trial_row)

        # Card footer
        form.addSpacing(10)
        footer = _text(
            "Admin Controlled  •  Session Control  •  Profile Isolation",
            10, "#4a6478")
        footer.setAlignment(Qt.AlignCenter)
        form.addWidget(footer)

        right_col.addWidget(card, 0, Qt.AlignHCenter)
        right_col.addStretch(1)
        shell.addLayout(right_col, 52)

        # Final layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(bg)

    def showEvent(self, event):
        """Use the native Windows dark caption bar via DWM."""
        super().showEvent(event)
        if sys.platform != "win32":
            return
        try:
            import ctypes
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
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
        editor.setEchoMode(
            QLineEdit.Normal if visible else QLineEdit.Password)
        button.setText("Hide" if visible else "Show")
        button.setAccessibleName(
            ("Hide " if visible else "Show ") + label.lower())

    def values(self):
        return {key: editor.text() for key, editor in self.inputs.items()}
