# Windows Preview Build

The Windows GitHub Actions workflow packages the PySide6/Qt WebEngine proof of concept using PyInstaller into a portable folder. The resulting artifact is available from the workflow run for authorized GitHub users.

## Status and limitations
- This is a development preview, **not** an online bootstrap installer or publicly published release.
- The output is a directory with an .exe and Qt dependencies, not a 1–5 MB standalone browser.
- The build does not support Chromium 148+ runtime switching, safe enterprise authentication, server-issued emergency tokens, cloud management, proxies or session transfer.
- No automatic client updates are enabled.
- Do not distribute to end users until Windows runtime smoke testing, code signing, sandbox audits and packaging checks pass.
- Android remains on hold. No AI assistant is included.

## Build locally
From the repository root on Windows with Python 3.12:
```powershell
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name DevSeaTechBrowserPreview --paths src --collect-all PySide6.QtWebEngineCore --collect-all PySide6.QtWebEngineWidgets src/devseatech_browser/app.py
```

Output: `dist/DevSeaTechBrowserPreview/DevSeaTechBrowserPreview.exe`

This initial packaging workflow validates creation of an executable, **not** GUI operation or security compliance.
