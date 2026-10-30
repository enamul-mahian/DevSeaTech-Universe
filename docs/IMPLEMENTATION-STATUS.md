# Implementation Status

As of 2026-10-30. This file tracks real, verified progress. A feature is only
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
| AF-02 Profile Backup/Restore | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/backup.py`; 10 tests in `tests/test_backup.py` (encrypt round-trip, wrong-key, tamper, retention, atomic write) pass locally |
| GUI runtime smoke harness | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | `tests/smoke/gui_smoke.py` runs offscreen → "SMOKE OK"; CI `linux-smoke.yml` added |
| CI: real encryption tests | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | `python-tests.yml` now installs `cryptography` so AF-02 crypto tests run, not skip |
| AF-01 Crash Recovery & Session Restore | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/session_restore.py`; 8 tests in `tests/test_session_restore.py`; periodic auto-save + atomic write + clean-exit marker; restore offered on next launch |
| AF-03 Profile Health Check | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/profile_health.py`; 12 tests in `tests/test_profile_health.py`; checks dir/storage/cache/symlinks/size/cookie-db; non-destructive |
| AF-04 Engine Compatibility Checker | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/engine_compat.py`; 11 tests in `tests/test_engine_compat.py`; checks Python/PySide6/WebEngine/platform/sandbox/display/disk/schema |
| AF-05 Download Manager | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/download_manager.py`; 13 tests in `tests/test_download_manager.py`; status tracking, pause/resume/cancel, persistence, risky-extension check, filename sanitization |
| AF-06 Secure Password Vault | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/password_vault.py`; 13 tests in `tests/test_password_vault.py`; Fernet+scrypt encrypted storage, per-profile vault, add/remove/list/export, lock/unlock |
| AF-07 Profile Import/Export/Clone | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/profile_migration.py`; 9 tests in `tests/test_profile_migration.py`; encrypted export/import roundtrip, clone with cache exclusion, path traversal protection |
| AF-08 Proxy Health Monitor | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/proxy_health.py`; 11 tests in `tests/test_proxy_health.py`; TCP connectivity check, config validation, URL parsing, system proxy detection |
| AF-09 Resource Manager | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/resource_manager.py`; 13 tests in `tests/test_resource_manager.py`; per-profile CPU/RAM/disk monitoring, policy thresholds, report formatting |
| AF-10 License Renewal Reminder | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/license_reminder.py`; 11 tests in `tests/test_license_reminder.py`; server-time expiration check, trial/standard thresholds, persistence |
| AF-11 Profile Templates | ✅ | ✅ | ✅ | n/a | ⬜ | ⬜ | `src/devseatech_browser/profile_templates.py`; 13 tests in `tests/test_profile_templates.py`; CRUD, blocked-field stripping, apply to profile, slug naming |

Verified locally this session: full suite **92/92 pass** (`PYTHONPATH=src python -m unittest discover -s tests`), including AF-02 encryption; offscreen GUI smoke exits 0 and constructs a Qt WebEngine window.

## Existing baseline (unchanged, preserved)
- Desktop browser: `src/devseatech_browser/{app,login_ui,recovery,update_policy}.py` — scrypt master/admin auth, per-profile isolation, session timer, branded neon login, fail-closed auto-update logic. 7 original tests still pass.
- Docs: license (720h server-time), themes/privacy, installer, release/update policy, milestone 01.

## 18 approved additional features (AF-01 … AF-18)
Source: `docs/APPROVED-ADDITIONAL-FEATURES.md`. All Spec ✅; implementation per the owner's delivery order (foundation first).

| ID | Feature | Status |
|---|---|---|
| AF-01 | Crash Recovery & Session Restore | **Impl + Unit** |
| AF-02 | Automatic Local Profile Backup | **Impl + Unit** |
| AF-03 | Profile Health Check | **Impl + Unit** |
| AF-04 | Engine Compatibility Checker | **Impl + Unit** |
| AF-05 | Download Manager | **Impl + Unit** |
| AF-06 | Secure Password Vault | **Impl + Unit** |
| AF-07 | Profile Import/Export/Clone | **Impl + Unit** |
| AF-08 | Proxy Health Monitor | **Impl + Unit** |
| AF-09 | Resource Manager | **Impl + Unit** |
| AF-10 | License Renewal Reminder | **Impl + Unit** |
| AF-11 | Profile Templates | **Impl + Unit** |
| AF-12 | Permission Manager | Spec |
| AF-13 | Security & Activity Logs | Spec |
| AF-14 | Browser Diagnostics & Repair | Spec |
| AF-15 | Workspace & Group Management | Spec |
| AF-16 | Keyboard Shortcuts Manager | Spec |
| AF-17 | Website Translation | Spec |
| AF-18 | Accessibility Settings | Spec |

## Web platform (parked, branch `development/web-platform-phase2`, commit f7eaeeb)
Commercial platform is item #3 in the approved delivery order, so it is parked
after a first scaffold:
- pnpm monorepo (does not touch the Python browser).
- `packages/ui` cosmic/neon design system (Dark/Light/Auto, reduced-motion starfield, glass primitives).
- `packages/contracts` license/device/plan/api zod schemas (server-authoritative 720h logic) with unit tests.
- `apps/web` public homepage + page stubs.
- Not yet: dependency install + build verification, admin dashboard, API app.

## Not done / honest gaps
- No security review on any feature yet (Sec ⬜ across the board).
- AF-02 encryption uses `cryptography` Fernet with a scrypt-derived key; OS-backed
  keystore integration (brief requirement) is not yet wired — passphrase is
  supplied by the caller.
- Web platform dependencies are not installed or build-verified in CI.
- No deployment, no payments, no real release. Source repo is currently public
  (owner's call); brief/docs recommend private.
