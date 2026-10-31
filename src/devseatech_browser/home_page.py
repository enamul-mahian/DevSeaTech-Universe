"""DevSeaTech Universe browser home page.

Generates a local HTML new-tab page with:
- DS logo (embedded as base64)
- Google search bar
- Speed dial tiles for frequently visited sites
- Cosmic dark theme matching the login UI
"""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import NamedTuple

ASSETS_DIR = Path(__file__).parent / "assets"
SPEED_DIAL_FILE = Path.home() / ".devseatech-browser" / "speed_dial.json"

# Default speed dial entries
DEFAULT_SPEED_DIAL = [
    {"title": "Google", "url": "https://www.google.com", "icon": "G"},
    {"title": "YouTube", "url": "https://www.youtube.com", "icon": "▶"},
    {"title": "GitHub", "url": "https://github.com", "icon": "⌥"},
    {"title": "Gmail", "url": "https://mail.google.com", "icon": "✉"},
    {"title": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "W"},
    {"title": "Reddit", "url": "https://www.reddit.com", "icon": "R"},
    {"title": "Stack Overflow", "url": "https://stackoverflow.com", "icon": "S"},
    {"title": "Twitter / X", "url": "https://x.com", "icon": "𝕏"},
]


class SpeedDialEntry(NamedTuple):
    title: str
    url: str
    icon: str


def load_speed_dial() -> list[SpeedDialEntry]:
    """Load user speed dial; fall back to defaults."""
    try:
        data = json.loads(SPEED_DIAL_FILE.read_text("utf-8"))
        return [SpeedDialEntry(**e) for e in data]
    except (OSError, ValueError, KeyError, TypeError):
        return [SpeedDialEntry(**e) for e in DEFAULT_SPEED_DIAL]


def save_speed_dial(entries: list[SpeedDialEntry]) -> None:
    """Persist speed dial entries."""
    SPEED_DIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    SPEED_DIAL_FILE.write_text(
        json.dumps([e._asdict() for e in entries], indent=2),
        encoding="utf-8",
    )


def _logo_base64() -> str:
    """Read the DS logo PNG and return a data URI."""
    logo_path = ASSETS_DIR / "ds_logo.png"
    if not logo_path.exists():
        return ""
    data = logo_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generate_home_html(entries: list[SpeedDialEntry] | None = None) -> str:
    """Return a self-contained HTML string for the home page."""
    if entries is None:
        entries = load_speed_dial()
    logo_uri = _logo_base64()

    tiles_html = ""
    for e in entries:
        tiles_html += f"""
        <a class="tile" href="{html.escape(e.url)}" title="{html.escape(e.title)}">
            <div class="tile-icon">{html.escape(e.icon)}</div>
            <div class="tile-label">{html.escape(e.title)}</div>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DevSeaTech Universe</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    min-height: 100vh;
    background: radial-gradient(ellipse at 50% 20%, #0d2a4a 0%, #071327 55%, #030b18 100%);
    color: #e4f7ff;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}}

/* stars */
body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.6), transparent),
        radial-gradient(1px 1px at 25% 40%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1.5px 1.5px at 50% 10%, rgba(100,220,255,0.7), transparent),
        radial-gradient(1px 1px at 70% 30%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 85% 55%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1.5px 1.5px at 40% 70%, rgba(100,220,255,0.5), transparent),
        radial-gradient(1px 1px at 60% 80%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 15% 90%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 90% 85%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1.2px 1.2px at 35% 25%, rgba(100,220,255,0.6), transparent);
    pointer-events: none;
    z-index: 0;
}}

.container {{
    position: relative;
    z-index: 1;
    text-align: center;
    width: 100%;
    max-width: 720px;
    padding: 20px;
}}

.logo {{
    margin-bottom: 12px;
}}

.logo img {{
    height: 120px;
    width: auto;
    filter: drop-shadow(0 0 30px rgba(0, 210, 255, 0.3));
}}

.brand-text {{
    font-size: 16px;
    color: #00d4ff;
    letter-spacing: 6px;
    text-transform: uppercase;
    margin-bottom: 36px;
    font-weight: 300;
}}

/* search bar */
.search-box {{
    position: relative;
    margin-bottom: 48px;
}}

.search-box input {{
    width: 100%;
    padding: 16px 52px 16px 52px;
    background: rgba(16, 41, 71, 0.85);
    border: 1px solid rgba(0, 180, 220, 0.35);
    border-radius: 28px;
    color: #e4f7ff;
    font-size: 16px;
    outline: none;
    transition: border-color 0.3s, box-shadow 0.3s;
}}

.search-box input:focus {{
    border-color: #00d4ff;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.25);
}}

.search-box input::placeholder {{
    color: #6fa8c8;
}}

.search-icon {{
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    color: #6fa8c8;
    pointer-events: none;
}}

.search-btn {{
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    background: linear-gradient(135deg, #0891b2, #06b6d4);
    border: none;
    border-radius: 22px;
    padding: 10px 20px;
    color: white;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.3s;
}}

.search-btn:hover {{
    background: linear-gradient(135deg, #06b6d4, #22d3ee);
}}

/* speed dial grid */
.speed-dial {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    max-width: 560px;
    margin: 0 auto;
}}

.tile {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px 8px 14px;
    background: rgba(16, 41, 71, 0.6);
    border: 1px solid rgba(0, 180, 220, 0.15);
    border-radius: 16px;
    text-decoration: none;
    color: #c8ecf8;
    transition: transform 0.2s, border-color 0.3s, box-shadow 0.3s, background 0.3s;
    cursor: pointer;
}}

.tile:hover {{
    transform: translateY(-4px);
    border-color: rgba(0, 210, 255, 0.5);
    box-shadow: 0 8px 24px rgba(0, 180, 220, 0.2);
    background: rgba(16, 50, 85, 0.75);
}}

.tile-icon {{
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(8, 105, 163, 0.8), rgba(6, 42, 82, 0.9));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 700;
    color: #65dcff;
    border: 1px solid rgba(0, 180, 220, 0.25);
}}

.tile-label {{
    font-size: 12px;
    font-weight: 500;
    color: #a0d4ea;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}}

/* footer */
.footer {{
    position: fixed;
    bottom: 16px;
    color: #3a6a86;
    font-size: 12px;
    letter-spacing: 1px;
}}

@media (max-width: 600px) {{
    .speed-dial {{ grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .logo img {{ height: 80px; }}
}}
</style>
</head>
<body>

<div class="container">
    <div class="logo">
        {"<img src='" + logo_uri + "' alt='DevSeaTech'>" if logo_uri else "<div style='font-size:48px;color:#00d4ff;font-weight:bold'>DevSeaTech</div>"}
    </div>
    <div class="brand-text">Secure Browser Platform</div>

    <div class="search-box">
        <span class="search-icon">🔍</span>
        <form action="https://www.google.com/search" method="get">
            <input type="text" name="q" placeholder="Search the web..." autofocus>
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>

    <div class="speed-dial">
        {tiles_html}
    </div>
</div>

<div class="footer">DevSeaTech Universe — Secure Browsing</div>

</body>
</html>"""


def get_home_page_url() -> str:
    """Write the home page HTML to a temp file and return its file:// URL."""
    cache_dir = Path.home() / ".devseatech-browser" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    home_file = cache_dir / "home.html"
    home_file.write_text(generate_home_html(), encoding="utf-8")
    # Path.as_uri() requires Python 3.13+; fall back for older versions.
    if hasattr(home_file, "as_uri"):
        return home_file.as_uri()
    # Manual file:// URI construction (works on Windows and Linux)
    import urllib.parse
    return "file:///" + urllib.parse.quote(str(home_file).replace("\\", "/"), safe="/:@")
