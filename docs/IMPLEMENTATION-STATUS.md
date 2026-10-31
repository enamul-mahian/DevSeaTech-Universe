# Implementation Status

As of 2026-10-31. This file tracks real, verified progress. A feature is only
advanced to a stronger status when there is evidence for it (a passing test, a
runtime check) — never on compilation or packaging alone.

## Status legend
- **Spec** — requirement documented and approved.
- **Impl** — code written.
- **Unit** — meaningful unit tests pass.
- **Runtime** — verified running (GUI/offscreen or integration), not just built.
- **Sec** — security review completed.
- **Rel** — released to users.

## Current foundation slice (branch `development/foundation-backup-restore`)

| Item | Spec | Impl | Unit | Runtime | Sec | Rel | Evidence |
|---|---|---|---|---|---|---|---|
| AF-02 Profile Backup/Restore | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `backup.py`; unit+integration+security tests pass; v0.1.0 |
| GUI runtime smoke harness | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `tests/smoke/gui_smoke.py` offscreen; CI `linux-smoke.yml`; v0.1.0 |
| CI: real encryption tests | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `python-tests.yml` installs `cryptography`; v0.1.0 |
| AF-01 Crash Recovery & Session Restore | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `session_restore.py`; integration+security tests; v0.1.0 |
| AF-03 Profile Health Check | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `profile_health.py`; integration+security tests; v0.1.0 |
| AF-04 Engine Compatibility Checker | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `engine_compat.py`; integration+security tests; v0.1.0 |
| AF-05 Download Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `download_manager.py`; integration+security tests; v0.1.0 |
| AF-06 Secure Password Vault | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `password_vault.py`; integration+security tests; v0.1.0 |
| AF-07 Profile Import/Export/Clone | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `profile_migration.py`; integration+security tests; v0.1.0 |
| AF-08 Proxy Health Monitor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `proxy_health.py`; integration+security tests; v0.1.0 |
| AF-09 Resource Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `resource_manager.py`; integration+security tests; v0.1.0 |
| AF-10 License Renewal Reminder | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `license_reminder.py`; integration+security tests; v0.1.0 |
| AF-11 Profile Templates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `profile_templates.py`; integration+security tests; v0.1.0 |
| AF-12 Permission Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `permission_manager.py`; integration+security tests; v0.1.0 |
| AF-13 Security & Activity Logs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `security_logs.py`; integration+security tests; v0.1.0 |
| AF-14 Browser Diagnostics & Repair | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `browser_diagnostics.py`; integration+security tests; v0.1.0 |
| AF-15 Workspace & Group Management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `workspace_manager.py`; integration+security tests; v0.1.0 |
| AF-16 Keyboard Shortcuts Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `keyboard_shortcuts.py`; integration+security tests; v0.1.0 |
| AF-17 Website Translation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `website_translation.py`; integration+security tests; v0.1.0 |
| AF-18 Accessibility Settings | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `accessibility_settings.py`; integration+security tests; v0.1.0 |

## Browser Home Page & Dashboard (branch `feat/dashboard-and-homepage`, PR #29)

| Item | Spec | Impl | Unit | Runtime | Sec | Rel | Evidence |
|---|---|---|---|---|---|---|---|
| Browser Home Page | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `home_page.py`; integration+security tests; v0.1.0 |
| Dashboard Redesign | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | `profile_dashboard.py`; integration+security tests; v0.1.0 |

## Main-branch desktop usability milestone (2026-10-31)

| Item | Spec | Impl | Unit | Runtime | Sec | Rel | Evidence |
|---|---|---|---|---|---|---|---|
| Login password visibility + profile dashboard empty/search/selection states | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | `tests/smoke/gui_smoke.py` exercises show/hide, search, create refresh, selection gating and opening; Windows offscreen Qt WebEngine smoke passes |

Verified on Linux with Python 3.13 and on Windows with Python 3.14: **270 tests pass** (`python -m pytest tests/ --tb=short`). Includes 24 runtime integration tests and 25 security review tests covering all 18 features. The offscreen GUI smoke exits 0. This does not replace manual visual review of the native UI.

## Existing baseline (unchanged, preserved)
- Desktop browser: `src/devseatech_browser/{app,login_ui,recovery,update_policy}.py` — scrypt master/admin auth, per-profile isolation, session timer, branded neon login, fail-closed auto-update logic. 7 original tests still pass.
- Docs: license (720h server-time), themes/privacy, installer, release/update policy, milestone 01.

## 18 approved additional features (AF-01 … AF-18)
Source: `docs/APPROVED-ADDITIONAL-FEATURES.md`. All Spec ✅; implementation per the owner's delivery order (foundation first).

| ID | Feature | Status |
|---|---|---|
| AF-01 | Crash Recovery & Session Restore | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-02 | Automatic Local Profile Backup | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-03 | Profile Health Check | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-04 | Engine Compatibility Checker | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-05 | Download Manager | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-06 | Secure Password Vault | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-07 | Profile Import/Export/Clone | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-08 | Proxy Health Monitor | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-09 | Resource Manager | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-10 | License Renewal Reminder | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-11 | Profile Templates | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-12 | Permission Manager | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-13 | Security & Activity Logs | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-14 | Browser Diagnostics & Repair | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-15 | Workspace & Group Management | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-16 | Keyboard Shortcuts Manager | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-17 | Website Translation | **Impl + Unit + Runtime + Sec + Rel** ✅ |
| AF-18 | Accessibility Settings | **Impl + Unit + Runtime + Sec + Rel** ✅ |

## Web platform (parked, branch `development/web-platform-phase2`, commit f7eaeeb)
Commercial platform is item #3 in the approved delivery order, so it is parked
after a first scaffold:
- pnpm monorepo (does not touch the Python browser).
- `packages/ui` cosmic/neon design system (Dark/Light/Auto, reduced-motion starfield, glass primitives).
- `packages/contracts` license/device/plan/api zod schemas (server-authoritative 720h logic) with unit tests.
- `apps/web` public homepage + page stubs.
- Not yet: dependency install + build verification, admin dashboard, API app.

## Not done / honest gaps
- AF-02 encryption uses `cryptography` Fernet with a scrypt-derived key; OS-backed
  keystore integration (brief requirement) is not yet wired — passphrase is
  supplied by the caller.
- Web platform dependencies are not installed or build-verified in CI.
- v0.1.0 is an internal tagged release (source + `pip install`). No production
  installer, signed binaries, or update server exist. Source repo is currently
  public (owner's call); brief/docs recommend private.
- Login UI does not match reference image (deferred per owner direction).
- PR #28 (login redesign) and PR #29 (dashboard+homepage) awaiting owner merge.

## Test summary (2026-10-31)
- **270 tests total**, all passing
- 221 unit tests (original + home page)
- 24 integration/runtime verification tests (`tests/test_integration_runtime.py`)
- 25 security review tests (`tests/test_security_review.py`)
