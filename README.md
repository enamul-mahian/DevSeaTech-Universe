# DevSeaTech Browser

A planned Windows and Linux Chromium-based, multi-version managed browser. **Development baseline; not a functional browser or production deployment.**

## Confirmed product requirements
- Chromium engine selection from version 148 onward, where verified compatible builds are available; install and remove engines.
- One master browser login grants access to all locally isolated profiles.
- Separate administrative authentication for settings, extension changes, profile policies, engine changes, and site-session transfer.
- Session duration and timezone-based allowed-hours controls; emergency one-use device-bound token uses the existing timer rules.
- Separate per-profile cookies, caches, storage, history, proxy configuration, browser identity, and engine selection.
- HTTP, HTTPS, and SOCKS5 proxies; install-time administrator-approved extensions automatically applied to new profiles.
- Optional Google/Microsoft sign-in for a future independent encrypted sync service, not Chrome Sync.
- Site-specific, encrypted export/import between authorized local profiles (e.g. Chromium 150 to 151) for compatible cookies, storage, cache, and tabs. Never bypass website authentication, expiration, revocation, or device-bound restrictions.
- Future DevSeaTech cloud enrollment, signed setup/policies, login verification, remote profile management, and **consent-based, view-only** remote support.
- Branded DevSeaTech login screen with subtle neon motion and company information.
- **No AI assistant. Android development on hold.**

## Branding
Company: DevSeaTech  
Telephone: +8801805839123  
Email: devseatech60@gmail.com  
Website: https://www.devseatech.com

The official logo asset must be added from the owner-approved source before publishing a branded binary.

## Security principles
A verified and signed engine/runtime is required; preserve platform sandboxes. Keep engine libraries shared but profile storage isolated. Encrypt secrets with OS-backed key storage; do not sync cookies or credentials to the management server by default. Profiles are not portable by simply copying Chromium data directories. Remote viewing needs explicit, revocable, per-session consent with a visible indicator. Signed policy is verified before applying. A system administrator can potentially bypass app-only timers; OS-managed enforcement needs separate work.

## Workstreams
1. Build-system and Chromium/CEF version feasibility (including binary redistribution licenses).
2. Desktop browser shell (Windows and Linux).
3. Engine manager and process isolation.
4. Profile isolation, proxy and identity management.
5. Secure master/admin login and timing policy.
6. Extension policy management.
7. Website session transfer with compatibility validation and rollback.
8. Future cloud setup and management service.
9. QA, security review, packaging and release.

## Current status
Repository initialization only. No browser executable, real authentication server, or deployment has been delivered.
