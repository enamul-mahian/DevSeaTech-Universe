# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for DevSeaTech Browser — Windows x64.

Usage (from repo root):
    pyinstaller --noconfirm packaging/pyinstaller-windows.spec

Builds a one-folder bundle under dist/DevSeaTechBrowser/.
"""

from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"
ASSETS = SRC / "devseatech_browser" / "assets"

a = Analysis(
    [str(SRC / "devseatech_browser" / "app.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        (str(ASSETS), "devseatech_browser/assets") if ASSETS.exists() else (str(SRC), "src"),
    ],
    hiddenimports=[
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "devseatech_browser.login_ui",
        "devseatech_browser.profile_dashboard",
        "devseatech_browser.home_page",
        "devseatech_browser.backup",
        "devseatech_browser.password_vault",
        "devseatech_browser.security_logs",
        "devseatech_browser.permission_manager",
        "devseatech_browser.engine_compat",
        "devseatech_browser.proxy_health",
        "devseatech_browser.resource_manager",
        "devseatech_browser.download_manager",
        "devseatech_browser.keyboard_shortcuts",
        "devseatech_browser.website_translation",
        "devseatech_browser.accessibility_settings",
        "devseatech_browser.workspace_manager",
        "devseatech_browser.browser_diagnostics",
        "devseatech_browser.recovery",
        "devseatech_browser.session_restore",
        "devseatech_browser.update_policy",
        "devseatech_browser.license_reminder",
        "devseatech_browser.profile_health",
        "devseatech_browser.profile_migration",
        "devseatech_browser.profile_restore",
        "devseatech_browser.profile_templates",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DevSeaTechBrowser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ASSETS / "ds_logo.ico") if (ASSETS / "ds_logo.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DevSeaTechBrowser",
)
