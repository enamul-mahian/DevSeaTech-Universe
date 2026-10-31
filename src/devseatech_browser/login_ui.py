"""DevSeaTech Universe desktop login, English-only Qt UI.

Visual-only redesign matching the approved reference.
Existing authentication remains in app.py.
Trial and license activation controls are visual placeholders
until server-side licensing exists.
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QSize
from PySide6.QtGui import (QColor, QLinearGradient, QPainter, QPainterPath,
                          QPen, QPolygonF, QRadialGradient, QFont, QBrush,
                          QPixmap, QIcon)
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QStyle, QGraphicsDropShadowEffect,
    QSizePolicy, QCheckBox, QGridLayout,
)

# ─── Paths ───────────────────────────────────────────────────────────
_ASSETS = Path(__file__).parent / "assets"
_LOGO_PATH = _ASSETS / "ds_logo.png"

# ─── Palette ─────────────────────────────────────────────────────────
_CYAN = "#00d4ff"
_CYAN_BTN = "#00bbdd"
_DEEP = "#020a1a"
_TEXT = "#e8f4ff"
_DIM = "#7da4be"
_CARD_BG = "rgba(6, 16, 42, 235)"


class _Star:
    __slots__ = ('xf', 'yf', 'sz', 'ph', 'ba')
    def __init__(self):
        self.xf = random.random()
        self.yf = random.random() * 0.70
        self.sz = random.choice([0.6, 0.8, 1.0, 1.2, 1.6, 2.0])
        self.ph = random.uniform(0, math.tau)
        self.ba = random.randint(70, 230)


class CosmicBackground(QWidget):
    """Animated cosmic background with planet, mountains & water."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tick = 0
        self._stars = [_Star() for _ in range(280)]
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

        # Sky
        sky = QLinearGradient(0, 0, w * 0.3, h)
        sky.setColorAt(0.0, QColor("#010510"))
        sky.setColorAt(0.25, QColor("#051830"))
        sky.setColorAt(0.55, QColor("#081828"))
        sky.setColorAt(1.0, QColor("#020810"))
        p.fillRect(self.rect(), sky)

        # Nebula glow
        for cx, cy, rad, r, g, b, a in [
            (0.65, 0.10, 0.55, 0, 90, 200, 65),
            (0.15, 0.06, 0.30, 12, 40, 120, 35),
            (0.45, 0.55, 0.28, 5, 20, 80, 22),
        ]:
            nb = QRadialGradient(QPointF(w * cx, h * cy), w * rad)
            nb.setColorAt(0.0, QColor(r, g, b, a))
            nb.setColorAt(0.5, QColor(r // 2, g // 2, b // 2, a // 3))
            nb.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(self.rect(), nb)

        # ── Large planet (top-right) ──
        pcx, pcy = w * 0.72, h * 0.12
        pr = min(w, h) * 0.40
        pg = QRadialGradient(QPointF(pcx - pr * 0.2, pcy - pr * 0.1), pr * 1.2)
        pg.setColorAt(0.0, QColor(40, 115, 195, 115))
        pg.setColorAt(0.35, QColor(22, 75, 155, 90))
        pg.setColorAt(0.7, QColor(10, 45, 100, 60))
        pg.setColorAt(1.0, QColor(3, 12, 35, 20))
        p.setPen(Qt.NoPen); p.setBrush(pg)
        p.drawEllipse(QPointF(pcx, pcy), pr, pr)
        # Edge glows
        for gw, ga in [(1.22, 25), (1.15, 45), (1.08, 30)]:
            eg = QRadialGradient(QPointF(pcx, pcy), pr * gw)
            eg.setColorAt(0.80, QColor(0, 0, 0, 0))
            eg.setColorAt(0.92, QColor(0, 185, 255, ga))
            eg.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(eg)
            p.drawEllipse(QPointF(pcx, pcy), pr * gw, pr * gw)

        # Stars
        for s in self._stars:
            tw = 0.5 + 0.5 * math.sin(t * 0.05 + s.ph)
            a = int(s.ba * (0.3 + 0.7 * tw))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(210, 235, 255, a))
            p.drawEllipse(QPointF(s.xf * w, s.yf * h), s.sz, s.sz)

        # Mountains (4 layers)
        for by, py_, col, fr, amp in [
            (0.68, 0.38, QColor(16, 42, 80, 210), 1.9, 0.12),
            (0.76, 0.48, QColor(10, 30, 62, 230), 2.5, 0.10),
            (0.84, 0.58, QColor(5, 20, 45, 245), 3.1, 0.08),
            (1.02, 0.72, QColor(3, 10, 25, 255), 1.3, 0.06),
        ]:
            poly = QPolygonF([QPointF(0, h)])
            for j in range(41):
                x = (j / 40) * w
                yv = h * (py_ + amp * math.sin(j * 0.5 + fr)
                          + amp * 0.55 * math.sin(j * 1.3 + fr * 1.7)
                          + amp * 0.28 * math.sin(j * 2.8 + fr * 0.5))
                poly.append(QPointF(x, min(h * by, yv)))
            poly.append(QPointF(w, h)); poly.append(QPointF(0, h))
            p.setPen(Qt.NoPen); p.setBrush(col)
            p.drawPolygon(poly)

        # Water
        wy = h * 0.82
        wg = QLinearGradient(0, wy, 0, h)
        wg.setColorAt(0.0, QColor(5, 28, 65, 120))
        wg.setColorAt(0.5, QColor(3, 18, 50, 160))
        wg.setColorAt(1.0, QColor(2, 10, 30, 200))
        p.fillRect(QRectF(0, wy, w, h - wy), wg)
        for i in range(10):
            ry = wy + 6 + i * ((h - wy - 6) / 10)
            rx = w * (0.15 + 0.07 * math.sin(t * 0.025 + i * 0.8))
            rw = w * (0.09 + 0.05 * math.sin(t * 0.02 + i * 1.4))
            al = int(22 + 18 * math.sin(t * 0.035 + i))
            p.setPen(QPen(QColor(0, 195, 255, al), 1.2))
            p.drawLine(QPointF(rx, ry), QPointF(rx + rw, ry))

        # Horizon glow
        hg = QLinearGradient(0, wy - 18, 0, wy + 18)
        hg.setColorAt(0, QColor(0, 0, 0, 0))
        hg.setColorAt(0.5, QColor(0, 165, 235, 45))
        hg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, wy - 18, w, 36), hg)

        # Shooting stars
        for i in range(3):
            sp = 2.2 + i * 1.4
            ln = 115 + i * 28
            sx = (t * sp + i * 950) % (w + 500) - 250
            sy = h * (0.04 + i * 0.12) + sx * 0.04
            al = max(0, min(155, 155 - abs(sx - w * 0.5) // 4))
            if al > 10:
                tg = QLinearGradient(QPointF(sx, sy), QPointF(sx - ln, sy + ln * 0.2))
                tg.setColorAt(0.0, QColor(210, 245, 255, al))
                tg.setColorAt(1.0, QColor(210, 245, 255, 0))
                p.setPen(QPen(tg, 1.8)); p.drawLine(QPointF(sx, sy), QPointF(sx - ln, sy + ln * 0.2))

        p.end()


def _lbl(text, size=14, color=_TEXT, bold=False):
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(
        f"background:transparent;border:0;color:{color};"
        f"font-size:{size}px;font-weight:{'700' if bold else '400'};")
    return lbl


def _circle_icon(char: str, sz: int = 56):
    """Circle icon badge."""
    b = QLabel(char)
    b.setFixedSize(sz, sz)
    b.setAlignment(Qt.AlignCenter)
    b.setStyleSheet(
        f"background:rgba(0,160,220,0.12);"
        f"border:2px solid rgba(0,160,220,0.40);"
        f"border-radius:{sz // 2}px;"
        f"color:{_CYAN};font-size:{sz * 2 // 5}px;")
    return b


class _GlowCard(QFrame):
    """Card with bright multi-layer neon glow border."""
    def __init__(self, intensity=1.0, parent=None):
        super().__init__(parent)
        self._intensity = intensity

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(6, 6, -6, -6)
        r = 16
        layers = [
            (14, 20), (10, 35), (7, 55), (5, 80),
            (3, 110), (2, 150), (1.2, 190),
        ]
        for width, alpha in layers:
            a = int(alpha * self._intensity)
            p.setPen(QPen(QColor(0, 200, 255, a), width))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect, r, r)
        # Bright inner edge
        p.setPen(QPen(QColor(140, 235, 255, int(230 * self._intensity)), 1.6))
        p.drawRoundedRect(rect, r, r)
        p.end()


def _action_card(icon_char: str, title: str, subtitle: str):
    """Bottom action card (Start Trial / Reset Access / License Activation)."""
    card = QFrame()
    card.setStyleSheet(
        "QFrame{background:rgba(6,18,48,220);border:1.5px solid rgba(0,180,230,0.30);"
        "border-radius:12px;}")
    card.setMinimumHeight(110)
    lay = QVBoxLayout(card)
    lay.setAlignment(Qt.AlignCenter)
    lay.setContentsMargins(12, 14, 12, 10)
    lay.setSpacing(4)

    # Icon
    ic = QLabel(icon_char)
    ic.setAlignment(Qt.AlignCenter)
    ic.setStyleSheet(f"background:transparent;border:0;color:{_CYAN};font-size:28px;")
    lay.addWidget(ic)

    # Title
    tl = _lbl(title, 13, _TEXT, True)
    tl.setAlignment(Qt.AlignCenter)
    lay.addWidget(tl)

    # Subtitle
    sl = _lbl(subtitle, 11, _DIM)
    sl.setAlignment(Qt.AlignCenter)
    lay.addWidget(sl)

    # Arrow
    ar = QLabel("→")
    ar.setAlignment(Qt.AlignCenter)
    ar.setStyleSheet(f"background:transparent;border:0;color:{_CYAN};font-size:16px;")
    lay.addWidget(ar)

    return card


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
        self.setStyleSheet(f"QDialog{{background:{_DEEP};}}")

        is_login = title == "Master Login"
        is_setup = title == "First-Time Setup"

        bg = CosmicBackground(self)
        shell = QHBoxLayout(bg)
        shell.setContentsMargins(48, 32, 42, 24)
        shell.setSpacing(36)

        # ═══════════════════════════════════════
        #  LEFT — Logo + tagline + features (2-col) + contact + quote
        # ═══════════════════════════════════════
        left = QVBoxLayout()
        left.setSpacing(4)

        # ── DS Logo image ──
        logo_lbl = QLabel()
        if _LOGO_PATH.exists():
            pix = QPixmap(str(_LOGO_PATH))
            logo_lbl.setPixmap(pix.scaledToHeight(140, Qt.SmoothTransformation))
        else:
            # Fallback: text logo
            lf = QFont(); lf.setPixelSize(64); lf.setBold(True)
            logo_lbl.setFont(lf)
            logo_lbl.setText("DS")
        logo_lbl.setStyleSheet("background:transparent;border:0;")
        left.addWidget(logo_lbl)

        # "DevSeaTech" text under logo
        logo_text = QLabel("DevSeaTech")
        ltf = QFont(); ltf.setPixelSize(42); ltf.setBold(True)
        logo_text.setFont(ltf)
        logo_text.setStyleSheet("background:transparent;border:0;color:#ffffff;")
        left.addWidget(logo_text)

        # "Universe" in cyan
        uni = QLabel("Universe")
        uf = QFont(); uf.setPixelSize(28); uf.setBold(True)
        uni.setFont(uf)
        uni.setStyleSheet(f"background:transparent;border:0;color:{_CYAN};")
        left.addWidget(uni)

        left.addSpacing(10)

        # Tagline
        tag = QLabel("Your All-in-One Secure Browser Platform")
        tf = QFont(); tf.setPixelSize(20); tf.setBold(True)
        tag.setFont(tf)
        tag.setStyleSheet("background:transparent;border:0;color:#c0d8ea;")
        tag.setWordWrap(True)
        left.addWidget(tag)
        left.addSpacing(4)
        left.addWidget(_lbl(
            "Multi-profile browsing with centralized administration\n"
            "and flexible licensing.", 13, _DIM))

        left.addSpacing(18)

        # Features in 2-column grid (matching reference)
        feats = [
            ("✔", "Secure Browsing", "Safe, Fast and Reliable"),
            ("⚡", "Multi-Version Engine", "Chromium 148+ Support"),
            ("\U0001f465", "Multi-Profile System", "Work, Personal and More"),
            ("\U0001f9e9", "Pre-configured Extensions", "Boost Productivity"),
            ("\U0001f310", "Proxies & Privacy", "HTTP, HTTPS, SOCKS5"),
            ("⏱", "Session Time Control", "Stay Focused, Stay Productive"),
        ]
        feat_grid = QGridLayout()
        feat_grid.setSpacing(10)
        feat_grid.setContentsMargins(0, 0, 0, 0)
        for idx, (ico, head, det) in enumerate(feats):
            row_idx = idx // 2
            col_idx = idx % 2
            cell = QHBoxLayout()
            cell.setSpacing(12)
            cell.setContentsMargins(0, 0, 0, 0)
            cell.addWidget(_circle_icon(ico, 48), 0, Qt.AlignVCenter)
            col = QVBoxLayout(); col.setSpacing(1)
            col.addWidget(_lbl(head, 15, "#e8f4ff", True))
            col.addWidget(_lbl(det, 11, _DIM))
            cell.addLayout(col, 1)

            wrapper = QWidget()
            wrapper.setStyleSheet("background:transparent;")
            wrapper.setLayout(cell)
            feat_grid.addWidget(wrapper, row_idx, col_idx)

        left.addLayout(feat_grid)
        left.addStretch(1)

        # ── Bottom: Contact panel + Quote panel side by side ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        # Contact panel
        contact = _GlowCard(0.5)
        contact.setStyleSheet(
            "QFrame{background:rgba(4,16,42,215);border-radius:12px;}")
        cl = QVBoxLayout(contact)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(6)
        cl.addWidget(_lbl("Contact Information", 13, "#e8f4ff", True))
        cl.addSpacing(4)
        for sym, info in [
            ("✉", "devseatech60@gmail.com"),
            ("☎", "+8801805839123"),
            ("⊕", "www.devseatech.com"),
        ]:
            r = QHBoxLayout(); r.setSpacing(10)
            ic = _lbl(sym, 15, _CYAN); ic.setFixedWidth(24)
            r.addWidget(ic)
            r.addWidget(_lbl(info, 13, "#c0d8ea"))
            r.addStretch()
            cl.addLayout(r)
        bottom_row.addWidget(contact, 1)

        # Quote panel
        quote = QFrame()
        quote.setStyleSheet(
            "QFrame{background:rgba(4,16,42,200);border:1px solid rgba(0,160,220,0.20);"
            "border-radius:12px;}")
        ql = QVBoxLayout(quote)
        ql.setContentsMargins(18, 14, 18, 14)
        ql.setSpacing(6)

        q_mark = _lbl("““", 32, _CYAN, True)
        ql.addWidget(q_mark)
        q_text = _lbl("Technology\nfor a Safer\nDigital Tomorrow”", 16, "#e8f4ff", True)
        ql.addWidget(q_text)
        q_attr = _lbl("— DevSeaTech", 12, _DIM)
        ql.addWidget(q_attr)
        ql.addStretch()
        bottom_row.addWidget(quote, 1)

        left.addLayout(bottom_row)

        shell.addLayout(left, 46)

        # ═══════════════════════════════════════
        #  RIGHT — Auth card with tabs + action cards
        # ═══════════════════════════════════════
        rc = QVBoxLayout()
        rc.addStretch(1)

        card = _GlowCard(1.0)
        card.setObjectName("ac")
        card.setMaximumWidth(560)
        card.setMinimumWidth(400)
        card.setStyleSheet(f"""
            QFrame#ac {{
                background-color: {_CARD_BG};
                border-radius: 16px;
            }}
            QLineEdit {{
                color:#fff; background:#081c38;
                padding:15px 16px 15px 40px; min-height:26px;
                border:1.5px solid #1a4a6e; border-radius:10px;
                font-size:15px;
                selection-background-color:#0077cc;
            }}
            QLineEdit:focus {{ border:2px solid {_CYAN}; }}
            QLineEdit::placeholder {{ color:#3d6080; }}
            QPushButton#submit {{
                color:#fff;
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0088cc,stop:0.5 #00bbdd,stop:1 #00ddee);
                border:none; border-radius:10px;
                font-size:18px; font-weight:700; padding:16px;
            }}
            QPushButton#submit:hover {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #009de0,stop:0.5 #00ccee,stop:1 #00eeff);
            }}
            QPushButton#submit:pressed {{ background:#0077bb; }}
            QPushButton#tab_active {{
                color:#fff;
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0077bb,stop:1 #00aadd);
                border:none; border-radius:8px;
                font-size:14px; font-weight:700; padding:12px 20px;
            }}
            QPushButton#tab_inactive {{
                color:{_DIM};
                background:rgba(10,25,50,180);
                border:1px solid rgba(0,160,220,0.20);
                border-radius:8px;
                font-size:14px; font-weight:600; padding:12px 20px;
            }}
            QPushButton#tab_inactive:hover {{ color:#c0e0f0; }}
            QPushButton#vis {{
                background:rgba(0,160,220,0.08);
                border:1.5px solid rgba(0,160,220,0.35);
                border-radius:8px; color:{_CYAN};
                font-size:14px; font-weight:600;
                padding:15px 18px;
            }}
            QPushButton#vis:hover {{ background:rgba(0,160,220,0.18); }}
            QPushButton#link {{
                background:transparent; color:{_CYAN};
                font-size:13px; border:none; padding:4px;
            }}
            QPushButton#link:hover {{ color:#50eeff; }}
            QCheckBox {{
                color:#a0bcd0; font-size:13px;
                background:transparent; spacing:8px;
            }}
            QCheckBox::indicator {{
                width:18px; height:18px;
                border:1.5px solid #1a4a6e; border-radius:4px;
                background:#081c38;
            }}
            QCheckBox::indicator:checked {{
                background:{_CYAN}; border-color:{_CYAN};
            }}
        """)

        # Glow shadow
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(110)
        glow.setColor(QColor(0, 180, 255, 65))
        glow.setOffset(0, 0)
        card.setGraphicsEffect(glow)

        fm = QVBoxLayout(card)
        fm.setContentsMargins(42, 36, 42, 28)
        fm.setSpacing(5)

        # "WELCOME TO"
        wt = _lbl("W E L C O M E   T O", 13, _DIM, True)
        wt.setAlignment(Qt.AlignCenter)
        fm.addWidget(wt)
        fm.addSpacing(6)

        # "DevSeaTech Universe" — large
        ct = QLabel("DevSeaTech Universe")
        ctf = QFont(); ctf.setPixelSize(44); ctf.setBold(True)
        ct.setFont(ctf)
        ct.setStyleSheet("background:transparent;border:0;color:#ffffff;")
        ct.setAlignment(Qt.AlignCenter)
        ct.setWordWrap(True)
        fm.addWidget(ct)
        fm.addSpacing(3)

        st = _lbl("S E C U R E   B R O W S E R   A C C E S S", 11, _DIM, True)
        st.setAlignment(Qt.AlignCenter)
        fm.addWidget(st)

        fm.addSpacing(16)

        # ── Tab buttons: Master Login | Administrator ──
        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)

        tab_master = QPushButton("\U0001f512  Master Login")
        tab_master.setObjectName("tab_active")
        tab_master.setCursor(Qt.PointingHandCursor)
        tab_row.addWidget(tab_master, 1)

        tab_admin = QPushButton("\U0001f464  Administrator")
        tab_admin.setObjectName("tab_inactive")
        tab_admin.setCursor(Qt.PointingHandCursor)
        tab_row.addWidget(tab_admin, 1)

        fm.addLayout(tab_row)
        fm.addSpacing(14)

        # Fields
        for label_text, secret in fields:
            editor = QLineEdit()
            editor.setPlaceholderText("\U0001f511  Enter " + label_text.lower())
            editor.returnPressed.connect(self.accept)
            self.inputs[label_text] = editor

            if secret:
                editor.setEchoMode(QLineEdit.Password)
                fr = QHBoxLayout(); fr.setSpacing(8)
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
            fm.addSpacing(6)

        # Remember this device + Forgot password
        ck_row = QHBoxLayout()
        remember_cb = QCheckBox("Remember this device")
        remember_cb.setChecked(True)
        ck_row.addWidget(remember_cb)
        ck_row.addStretch()

        if is_login:
            forgot = QPushButton("Forgot password?")
            forgot.setObjectName("link")
            forgot.setCursor(Qt.PointingHandCursor)
            forgot.setStyleSheet(
                f"background:transparent;color:{_CYAN};font-size:13px;"
                f"border:none;padding:2px;")
            forgot.setEnabled(False)  # placeholder
            ck_row.addWidget(forgot)

        fm.addLayout(ck_row)
        fm.addSpacing(12)

        # Submit button
        sub = QPushButton(
            "Create Credentials" if is_setup else "Login to Universe  →")
        sub.setObjectName("submit")
        sub.setMinimumHeight(56)
        sub.setCursor(Qt.PointingHandCursor)
        sub.clicked.connect(self.accept)
        fm.addWidget(sub)

        fm.addSpacing(12)

        # ── OR divider ──
        or_row = QHBoxLayout()
        or_row.setSpacing(12)
        sep1 = QFrame(); sep1.setFixedHeight(1)
        sep1.setStyleSheet("background:rgba(0,160,220,0.18);")
        or_row.addWidget(sep1, 1)
        or_lbl = _lbl("OR", 12, "#4a6a80", True)
        or_lbl.setAlignment(Qt.AlignCenter)
        or_lbl.setFixedWidth(30)
        or_row.addWidget(or_lbl)
        sep2 = QFrame(); sep2.setFixedHeight(1)
        sep2.setStyleSheet("background:rgba(0,160,220,0.18);")
        or_row.addWidget(sep2, 1)
        fm.addLayout(or_row)

        fm.addSpacing(12)

        # ── 3 action cards at bottom ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)

        c1 = _action_card("⏱", "Start Trial",
                          "24h / 72h /\nCustom Hours")
        c2 = _action_card("\U0001f504", "Reset Access",
                          "Forgot both\npasswords?")
        c3 = _action_card("⚙", "License Activation",
                          "Activate with\nLicense Key")
        cards_row.addWidget(c1, 1)
        cards_row.addWidget(c2, 1)
        cards_row.addWidget(c3, 1)

        # Wire reset card click
        c2.mousePressEvent = lambda _: self.done(2)

        fm.addLayout(cards_row)

        rc.addWidget(card, 0, Qt.AlignHCenter)
        rc.addStretch(1)
        shell.addLayout(rc, 54)

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
