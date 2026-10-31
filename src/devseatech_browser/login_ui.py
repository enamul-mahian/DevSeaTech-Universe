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
                          QPen, QPolygonF, QRadialGradient, QFont, QBrush,
                          QPixmap)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QStyle, QGraphicsDropShadowEffect,
    QSizePolicy,
)


# ─── Palette ─────────────────────────────────────────────────────────
_CYAN = "#00d4ff"
_CYAN_MID = "#00a8d6"
_DEEP = "#020a1a"
_TEXT = "#e8f4ff"
_DIM = "#7da4be"


class _Star:
    __slots__ = ('xf', 'yf', 'sz', 'ph', 'ba')
    def __init__(self):
        self.xf = random.random()
        self.yf = random.random() * 0.72
        self.sz = random.choice([0.6, 0.8, 1.0, 1.2, 1.6, 2.2])
        self.ph = random.uniform(0, math.tau)
        self.ba = random.randint(70, 230)


class CosmicBackground(QWidget):
    """Rich animated cosmic background with large planet."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tick = 0
        self._stars = [_Star() for _ in range(300)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._adv)
        self.timer.start(50)

    def _adv(self):
        self.tick = (self.tick + 1) % 7200
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = max(1, self.width()), max(1, self.height())
        t = self.tick

        # Sky gradient
        sky = QLinearGradient(0, 0, w * 0.4, h)
        sky.setColorAt(0.0, QColor("#010510"))
        sky.setColorAt(0.3, QColor("#061a34"))
        sky.setColorAt(0.6, QColor("#091830"))
        sky.setColorAt(1.0, QColor("#020810"))
        p.fillRect(self.rect(), sky)

        # Nebulae (ambient glow areas)
        for cx, cy, rad, r, g, b, a in [
            (0.70, 0.12, 0.60, 0, 100, 220, 70),
            (0.20, 0.06, 0.35, 15, 50, 140, 40),
            (0.50, 0.50, 0.30, 5, 25, 90, 25),
        ]:
            nb = QRadialGradient(QPointF(w * cx, h * cy), w * rad)
            nb.setColorAt(0.0, QColor(r, g, b, a))
            nb.setColorAt(0.5, QColor(r // 2, g // 2, b // 2, a // 3))
            nb.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(self.rect(), nb)

        # ── BIG PLANET (top-right, partially behind mountains) ──
        pcx, pcy = w * 0.72, h * 0.15
        pr = min(w, h) * 0.38  # MUCH bigger planet
        # Planet body
        pg = QRadialGradient(QPointF(pcx - pr * 0.25, pcy - pr * 0.15), pr * 1.2)
        pg.setColorAt(0.0, QColor(40, 120, 200, 120))
        pg.setColorAt(0.3, QColor(25, 80, 160, 100))
        pg.setColorAt(0.6, QColor(12, 50, 110, 80))
        pg.setColorAt(1.0, QColor(3, 15, 40, 30))
        p.setPen(Qt.NoPen); p.setBrush(pg)
        p.drawEllipse(QPointF(pcx, pcy), pr, pr)
        # Bright edge glow
        for gw, ga in [(1.25, 30), (1.18, 50), (1.12, 35)]:
            eg = QRadialGradient(QPointF(pcx, pcy), pr * gw)
            eg.setColorAt(0.78, QColor(0, 0, 0, 0))
            eg.setColorAt(0.90, QColor(0, 190, 255, ga))
            eg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(eg)
            p.drawEllipse(QPointF(pcx, pcy), pr * gw, pr * gw)
        # Ring
        p.setPen(QPen(QColor(80, 200, 255, 40), 2.0))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(pcx, pcy), pr * 2.0, pr * 0.45)

        # Stars
        for s in self._stars:
            tw = 0.5 + 0.5 * math.sin(t * 0.05 + s.ph)
            a = int(s.ba * (0.3 + 0.7 * tw))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(210, 235, 255, a))
            p.drawEllipse(QPointF(s.xf * w, s.yf * h), s.sz, s.sz)

        # Mountains (4 layers — taller, more dramatic)
        for by, py_, col, fr, amp in [
            (0.70, 0.40, QColor(18, 45, 85, 210), 1.9, 0.12),
            (0.78, 0.50, QColor(12, 32, 65, 230), 2.5, 0.10),
            (0.86, 0.60, QColor(6, 22, 48, 245), 3.1, 0.08),
            (1.02, 0.74, QColor(3, 12, 28, 255), 1.3, 0.06),
        ]:
            poly = QPolygonF([QPointF(0, h)])
            for j in range(41):
                x = (j / 40) * w
                yv = h * (py_ + amp * math.sin(j * 0.5 + fr)
                          + amp * 0.6 * math.sin(j * 1.3 + fr * 1.7)
                          + amp * 0.3 * math.sin(j * 2.8 + fr * 0.5))
                poly.append(QPointF(x, min(h * by, yv)))
            poly.append(QPointF(w, h)); poly.append(QPointF(0, h))
            p.setPen(Qt.NoPen); p.setBrush(col)
            p.drawPolygon(poly)

        # Water reflection
        wy = h * 0.82
        wg = QLinearGradient(0, wy, 0, h)
        wg.setColorAt(0.0, QColor(5, 30, 70, 120))
        wg.setColorAt(0.4, QColor(3, 20, 55, 160))
        wg.setColorAt(1.0, QColor(2, 12, 32, 200))
        p.fillRect(QRectF(0, wy, w, h - wy), wg)
        # Shimmer lines on water
        for i in range(12):
            ry = wy + 6 + i * ((h - wy - 6) / 12)
            rx = w * (0.15 + 0.08 * math.sin(t * 0.025 + i * 0.8))
            rw = w * (0.10 + 0.06 * math.sin(t * 0.02 + i * 1.4))
            al = int(25 + 20 * math.sin(t * 0.035 + i))
            p.setPen(QPen(QColor(0, 200, 255, al), 1.2))
            p.drawLine(QPointF(rx, ry), QPointF(rx + rw, ry))

        # Horizon glow
        hg = QLinearGradient(0, wy - 20, 0, wy + 20)
        hg.setColorAt(0, QColor(0, 0, 0, 0))
        hg.setColorAt(0.5, QColor(0, 170, 240, 50))
        hg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, wy - 20, w, 40), hg)

        # Shooting stars
        for i in range(3):
            sp = 2.2 + i * 1.4
            ln = 120 + i * 30
            sx = (t * sp + i * 950) % (w + 500) - 250
            sy = h * (0.04 + i * 0.12) + sx * 0.04
            al = max(0, min(160, 160 - abs(sx - w * 0.5) // 4))
            if al > 10:
                tg = QLinearGradient(QPointF(sx, sy), QPointF(sx - ln, sy + ln * 0.2))
                tg.setColorAt(0.0, QColor(210, 245, 255, al))
                tg.setColorAt(1.0, QColor(210, 245, 255, 0))
                p.setPen(QPen(tg, 2.0)); p.drawLine(QPointF(sx, sy), QPointF(sx - ln, sy + ln * 0.2))

        p.end()


def _lbl(text, size=14, color=_TEXT, bold=False):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(
        f"background:transparent;border:0;color:{color};"
        f"font-size:{size}px;font-weight:{'700' if bold else '400'};")
    return lbl


def _circle_icon(char: str, sz: int = 64):
    """Large circle icon badge with border."""
    b = QLabel(char)
    b.setFixedSize(sz, sz)
    b.setAlignment(Qt.AlignCenter)
    b.setStyleSheet(
        f"background:rgba(0,180,230,0.12);"
        f"border:2px solid rgba(0,180,230,0.45);"
        f"border-radius:{sz // 2}px;"
        f"color:{_CYAN};font-size:{sz * 2 // 5}px;")
    return b


class _GlowCard(QFrame):
    """Card with BRIGHT multi-layer neon glow border — matches reference."""
    def __init__(self, intensity=1.0, parent=None):
        super().__init__(parent)
        self._intensity = intensity

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(6, 6, -6, -6)
        r = 16
        # Glow layers — outer diffuse to inner bright (MUCH brighter than before)
        layers = [
            (16, 18), (12, 30), (9, 45), (6, 70),
            (4, 100), (2.5, 140), (1.5, 180),
        ]
        for width, alpha in layers:
            a = int(alpha * self._intensity)
            p.setPen(QPen(QColor(0, 200, 255, a), width))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect, r, r)
        # Very bright inner edge — almost white-cyan
        p.setPen(QPen(QColor(120, 230, 255, int(220 * self._intensity)), 1.8))
        p.drawRoundedRect(rect, r, r)
        p.end()


class BrandedLoginDialog(QDialog):
    """Field keys and return codes retain compatibility with app.py."""

    def __init__(self, title: str, fields: list[tuple[str, bool]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevSeaTech Universe — " + title)
        self.setWindowIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon))
        self.resize(1420, 880)
        self.setMinimumSize(1060, 700)
        self.inputs: dict[str, QLineEdit] = {}
        self.setStyleSheet("QDialog{background:#010714;}")

        is_login = title == "Master Login"
        is_setup = title == "First-Time Setup"

        bg = CosmicBackground(self)
        shell = QHBoxLayout(bg)
        shell.setContentsMargins(55, 40, 48, 30)
        shell.setSpacing(40)

        # ═══════════════════════════════════════
        #  LEFT — Brand + features + contact
        # ═══════════════════════════════════════
        left = QVBoxLayout()
        left.setSpacing(4)

        # ── Logo text (BIG) ──
        logo = QLabel("DevSeaTech")
        lf = QFont(); lf.setPixelSize(68); lf.setBold(True)
        logo.setFont(lf)
        logo.setStyleSheet("background:transparent;border:0;color:#ffffff;")
        left.addWidget(logo)

        uni = QLabel("Universe")
        uf = QFont(); uf.setPixelSize(38); uf.setBold(True)
        uni.setFont(uf)
        uni.setStyleSheet(f"background:transparent;border:0;color:{_CYAN};")
        left.addWidget(uni)

        left.addSpacing(20)

        # Tagline (bigger)
        tag = QLabel("Your secure digital workspace")
        tf = QFont(); tf.setPixelSize(26); tf.setBold(True)
        tag.setFont(tf)
        tag.setStyleSheet("background:transparent;border:0;color:#ffffff;")
        tag.setWordWrap(True)
        left.addWidget(tag)
        left.addSpacing(5)
        left.addWidget(_lbl(
            "Multi-profile browsing with centralized administration\n"
            "and flexible licensing.", 15, _DIM))

        left.addSpacing(24)

        # Features with LARGE circle icons
        feats = [
            ("\U0001f6e1", "Secure Browsing",
             "Protect browsing data and user access."),
            ("\U0001f465", "Multi-Profile System",
             "Isolated cookies, cache and sessions."),
            ("⚙", "Engine Management",
             "Multi-version runtime support: planned."),
            ("\U0001f310", "Proxies & Privacy",
             "HTTP, HTTPS and SOCKS5: planned."),
            ("⏱", "Session Time Control",
             "Administrator-managed sessions."),
        ]
        for ico, head, det in feats:
            row = QHBoxLayout()
            row.setSpacing(18)
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(_circle_icon(ico, 64), 0, Qt.AlignVCenter)
            col = QVBoxLayout(); col.setSpacing(2)
            col.addWidget(_lbl(head, 20, "#e8f4ff", True))
            col.addWidget(_lbl(det, 14, _DIM))
            row.addLayout(col, 1)
            left.addLayout(row)
            left.addSpacing(10)

        left.addStretch(1)

        # Contact panel with neon border (brighter)
        contact = _GlowCard(0.6)
        contact.setStyleSheet(
            "QFrame{background:rgba(4,16,42,215);border-radius:14px;}")
        cl = QVBoxLayout(contact)
        cl.setContentsMargins(24, 18, 24, 18)
        cl.setSpacing(8)
        cl.addWidget(_lbl("CONTACT INFORMATION", 13, _CYAN, True))
        cl.addSpacing(4)
        for sym, info in [
            ("✉", "devseatech60@gmail.com"),
            ("☎", "+8801805839123"),
            ("⊕", "www.devseatech.com"),
        ]:
            r = QHBoxLayout(); r.setSpacing(14)
            ic = _lbl(sym, 17, _CYAN); ic.setFixedWidth(26)
            r.addWidget(ic)
            r.addWidget(_lbl(info, 15, "#c8dced"))
            r.addStretch()
            cl.addLayout(r)
        left.addWidget(contact)

        shell.addLayout(left, 44)

        # ═══════════════════════════════════════
        #  RIGHT — Auth card with BRIGHT neon glow
        # ═══════════════════════════════════════
        rc = QVBoxLayout()
        rc.addStretch(1)

        card = _GlowCard(1.0)
        card.setObjectName("ac")
        card.setMaximumWidth(560)
        card.setMinimumWidth(420)
        card.setStyleSheet(f"""
            QFrame#ac {{
                background-color: rgba(4, 14, 38, 235);
                border-radius: 16px;
            }}
            QLineEdit {{
                color:#fff; background:#081c38;
                padding:16px 18px 16px 42px; min-height:28px;
                border:1.5px solid #1a4a6e; border-radius:10px;
                font-size:16px;
                selection-background-color:#0077cc;
            }}
            QLineEdit:focus {{ border:2px solid {_CYAN}; }}
            QLineEdit::placeholder {{ color:#3d6080; }}
            QPushButton#submit {{
                color:#fff;
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0088cc,stop:0.5 #00bbdd,stop:1 #00ddee);
                border:none; border-radius:10px;
                font-size:19px; font-weight:700; padding:18px;
            }}
            QPushButton#submit:hover {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #009de0,stop:0.5 #00ccee,stop:1 #00eeff);
            }}
            QPushButton#submit:pressed {{ background:#0077bb; }}
            QPushButton#vis {{
                background:rgba(0,160,220,0.08);
                border:1.5px solid rgba(0,160,220,0.35);
                border-radius:10px; color:{_CYAN};
                font-size:15px; font-weight:600;
                padding:16px 20px;
            }}
            QPushButton#vis:hover {{ background:rgba(0,160,220,0.18); }}
            QPushButton#link {{
                background:transparent; color:{_CYAN};
                font-size:14px; border:none; padding:4px;
                text-decoration:underline;
            }}
            QPushButton#link:hover {{ color:#50eeff; }}
        """)

        # Strong outer glow shadow
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(120)
        glow.setColor(QColor(0, 180, 255, 70))
        glow.setOffset(0, 0)
        card.setGraphicsEffect(glow)

        fm = QVBoxLayout(card)
        fm.setContentsMargins(48, 42, 48, 34)
        fm.setSpacing(6)

        # "WELCOME TO" — bigger
        wt = _lbl("WELCOME TO", 15, _DIM, True)
        wt.setAlignment(Qt.AlignCenter)
        fm.addWidget(wt)
        fm.addSpacing(6)

        # "DevSeaTech Universe" — LARGE centered (matching reference ~50px)
        ct = QLabel("DevSeaTech Universe")
        ctf = QFont(); ctf.setPixelSize(48); ctf.setBold(True)
        ct.setFont(ctf)
        ct.setStyleSheet("background:transparent;border:0;color:#ffffff;")
        ct.setAlignment(Qt.AlignCenter)
        ct.setWordWrap(True)
        fm.addWidget(ct)
        fm.addSpacing(4)

        st = _lbl("SECURE BROWSER ACCESS", 14, _DIM, True)
        st.setAlignment(Qt.AlignCenter)
        fm.addWidget(st)

        fm.addSpacing(28)

        # Fields
        for label_text, secret in fields:
            fm.addWidget(_lbl(label_text.upper(), 15, "#a0bcd0", True))
            fm.addSpacing(6)

            editor = QLineEdit()
            # Lock icon prefix via placeholder with lock symbol
            editor.setPlaceholderText("\U0001f512 Enter " + label_text.lower())
            editor.returnPressed.connect(self.accept)
            self.inputs[label_text] = editor

            if secret:
                editor.setEchoMode(QLineEdit.Password)
                fr = QHBoxLayout(); fr.setSpacing(10)
                fr.addWidget(editor, 1)
                vb = QPushButton("Show")
                vb.setObjectName("vis")
                vb.setCheckable(True)
                vb.setCursor(Qt.PointingHandCursor)
                vb.setAccessibleName("Show " + label_text.lower())
                vb.toggled.connect(
                    lambda v, f=editor, b=vb, n=label_text:
                    self._set_password_visibility(f, b, n, v))
                fr.addWidget(vb)
                fm.addLayout(fr)
            else:
                fm.addWidget(editor)
            fm.addSpacing(10)

        fm.addSpacing(16)

        # Submit button (bigger)
        sub = QPushButton(
            "Create Credentials" if is_setup else "Login to Universe  →")
        sub.setObjectName("submit")
        sub.setMinimumHeight(62)
        sub.setCursor(Qt.PointingHandCursor)
        sub.clicked.connect(self.accept)
        fm.addWidget(sub)

        # Links
        if is_login:
            fm.addSpacing(10)
            lrow = QHBoxLayout()
            lrow.addStretch()

            forgot = QPushButton("Forgot both passwords?")
            forgot.setObjectName("link")
            forgot.setCursor(Qt.PointingHandCursor)
            forgot.setEnabled(False)  # placeholder until recovery flow
            lrow.addWidget(forgot)

            sep_lbl = _lbl("|", 14, "#3a5a70")
            sep_lbl.setFixedWidth(24)
            sep_lbl.setAlignment(Qt.AlignCenter)
            lrow.addWidget(sep_lbl)

            reset = QPushButton("Reset preview access")
            reset.setObjectName("link")
            reset.setCursor(Qt.PointingHandCursor)
            reset.clicked.connect(lambda: self.done(2))
            lrow.addWidget(reset)

            lrow.addStretch()
            fm.addLayout(lrow)

        # Trial licensing info
        fm.addSpacing(16)
        tsep = QFrame(); tsep.setFixedHeight(1)
        tsep.setStyleSheet("background:rgba(0,160,220,0.20);")
        fm.addWidget(tsep)
        fm.addSpacing(14)

        tr = QHBoxLayout(); tr.setSpacing(16)
        ii = _lbl("ⓘ", 20, _CYAN); ii.setFixedWidth(28)
        tr.addWidget(ii, 0, Qt.AlignTop)
        tc = QVBoxLayout(); tc.setSpacing(4)
        tc.addWidget(_lbl(
            "TRIAL LICENSING  •  24h / 72h / custom hours",
            13, "#c8dced", True))
        tc.addWidget(_lbl(
            "License activation and server recovery will appear\n"
            "after their secure services are implemented.",
            12, "#5a7a90"))
        tr.addLayout(tc, 1)
        fm.addLayout(tr)

        # Footer
        fm.addSpacing(14)
        foot = _lbl(
            "Admin Controlled  •  Session Control  •  Profile Isolation",
            12, "#4a6478")
        foot.setAlignment(Qt.AlignCenter)
        fm.addWidget(foot)

        rc.addWidget(card, 0, Qt.AlignHCenter)
        rc.addStretch(1)
        shell.addLayout(rc, 56)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(bg)

    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform != "win32":
            return
        try:
            import ctypes
            hwnd = int(self.winId())
            v = ctypes.c_int(1)
            dwm = ctypes.windll.dwmapi.DwmSetWindowAttribute
            if dwm(hwnd, 20, ctypes.byref(v), ctypes.sizeof(v)) != 0:
                dwm(hwnd, 19, ctypes.byref(v), ctypes.sizeof(v))
        except (AttributeError, OSError, ValueError):
            return

    @staticmethod
    def _set_password_visibility(editor, button, label, visible):
        editor.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        button.setText("Hide" if visible else "Show")
        button.setAccessibleName(("Hide " if visible else "Show ") + label.lower())

    def values(self):
        return {k: e.text() for k, e in self.inputs.items()}
