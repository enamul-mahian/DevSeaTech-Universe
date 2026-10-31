# Packaging

Build instructions for DevSeaTech Browser desktop installers.

## Prerequisites

- Python 3.12+
- PySide6 >= 6.8
- PyInstaller
- (Windows) Visual C++ redistributable

## Build Commands

### Linux

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm packaging/pyinstaller-linux.spec
# Output: dist/DevSeaTechBrowser/DevSeaTechBrowser
```

### Windows

```powershell
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm packaging/pyinstaller-windows.spec
# Output: dist\DevSeaTechBrowser\DevSeaTechBrowser.exe
```

## CI Builds

- **Linux**: `.github/workflows/linux-package.yml` — builds on push to `development/packaging` or PR to main
- **Windows**: `.github/workflows/windows-preview.yml` — builds on push to `development/windows-build` or PR to main

Both workflows upload the build as a private CI artifact (7-day retention).

## Security Notes

- The application's Chromium sandbox stays **ON** in all builds
- Only CI smoke tests disable the sandbox (via environment variable)
- Builds are not signed — signing requires the owner's certificate
- Auto-update is **OFF** by default (fail-closed policy)
