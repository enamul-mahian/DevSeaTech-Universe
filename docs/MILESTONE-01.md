# Milestone 01 — Desktop Proof of Concept

## What is implemented
- Windows/Linux Python Qt WebEngine prototype with address bar and tabs.
- First-run master/admin password setup using scrypt password hashes.
- Master login on every application launch with three attempts.
- One master login allows access to all browser profiles.
- New profile creation requires administrator password.
- Separate persistent storage and cache paths for each profile.
- Basic session-duration timer which closes the app when expired.
- English-only UI and initial DevSeaTech color palette.

## Run locally
Install Python 3.11 or later. Create a virtual environment, run
`pip install -r requirements.txt`, then:
`PYTHONPATH=src python -m devseatech_browser.app` (Linux/macOS shells)
or `$env:PYTHONPATH="src"; python -m devseatech_browser.app` (PowerShell).

This prototype requires a desktop GUI and Qt WebEngine dependencies.

## Critical limitations
- Qt WebEngine uses its bundled Chromium runtime. **Chromium 148+ multi-engine management is NOT implemented.**
- This is NOT a hardened browser or a replacement for secure enterprise authentication.
- Login policies are local only; device-bound emergency tokens and server authentication are not implemented.
- Timezone schedules, proxy support, extensions, cloud sync and remote viewing are not implemented.
- No website-session export/import yet; do not manually copy sensitive cookies.
- A simple local session timer can be bypassed by a device administrator and is not suitable for enforcement.
- Browser identity spoofing and version switching are not implemented.
- Packaging, CI, malware protection and security audit are pending.
- Android remains on hold; no AI features.

## Next engineering gate
Before considering production deployment, select the Chromium/CEF engine
distribution strategy, harden sandboxing, implement verified update packages,
test profile isolation, and write a security threat model.
