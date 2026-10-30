# Approved Stability and Productivity Feature Expansion

Status: **Owner approved — 2026-10-30**. Requirements specification; implementation and testing remain pending.

## Scope
All previous DevSeaTech Universe requirements remain unchanged. The following 18 additional features are approved and must be developed without AI assistant functionality. Windows/Linux active; Android on hold.

| ID | Feature | Priority | Minimum acceptance criteria |
|---|---|---|---|
| AF-01 | Crash Recovery and Automatic Session Restore | Critical | Unexpected shutdown restores eligible tabs without exposing another profile's data; respects expired or revoked website sessions |
| AF-02 | Automatic Local Profile Backup | Critical | Scheduled encrypted profile snapshots, atomic writes, restore testing, size/retention limits, no plaintext authentication secrets |
| AF-03 | Profile Health Check | Critical | Detects inaccessible/corrupted data, reports actionable findings without destructive automatic repair |
| AF-04 | Engine Compatibility Checker | Critical | Checks runtime, storage schema, OS compatibility and sandbox requirements before engine switching |
| AF-05 | Download Manager | Critical | Download status/history, cancel/pause/resume only where supported, secure destination handling |
| AF-06 | Secure Password Vault | Critical | OS-backed encrypted storage, authorization for sensitive exports, no plaintext secret logging |
| AF-07 | Profile Import, Export and Clone | High | Explicit authorization; isolated storage; encrypted migration with rollback; website authentication validity not guaranteed |
| AF-08 | Proxy Health Monitor | High | Connection and configuration checks for HTTP, HTTPS, SOCKS5; identify possible DNS/IP leaks without collecting unrelated browsing |
| AF-09 | Resource Manager | High | Per-profile CPU, RAM and disk monitoring with low-overhead measurement and actionable limits |
| AF-10 | License Renewal Reminder | High | Notifications based on server-verified expiration, no silent auto-renewal or charges |
| AF-11 | Profile Templates | High | Admin-approved settings templates with no accidental sharing of cookies or passwords |
| AF-12 | Permission Manager | High | Site-by-site camera, microphone, geolocation and notifications, clear auditability |
| AF-13 | Security and Activity Logs | High | Privileged change and security-event auditing, sensitive-data redaction and retention rules |
| AF-14 | Browser Diagnostics and Repair | High | Read-only diagnostics by default; confirm, backup and rollback before repairs |
| AF-15 | Workspace and Group Management | Medium | Search/filter, grouping and safe bulk actions with authorization checks |
| AF-16 | Keyboard Shortcuts Manager | Medium | Customizable shortcuts, conflict validation, accessibility |
| AF-17 | Website Translation | Medium | Explicit website translation without changing English product UI; privacy disclosure for network translation |
| AF-18 | Accessibility Settings | Medium | Keyboard navigation, high contrast, scaling, reduced motion and screen-reader usability |

## Delivery order: stable and tested first
1. **Foundation quality gate:** Actual Windows GUI smoke tests, authentication/recovery, profile isolation, correct approved login/dashboard visuals, crash persistence, backup/restore and diagnostics. Stop treating a packaging-only CI success as runtime verification.
2. **Core controls:** Verified Chromium engine strategy and compatibility checker; per-profile proxy, permissions, secure password storage and downloads; safe profile migration and session restoration.
3. **Commercial platform:** Exactly 30-day paid licenses, 24/72/custom-hour trial policy, device-bound licensing, server authorization and payment gateway integration. Never enable real payments without approval.
4. **Operational improvements:** Profiles/templates/groups, resources, history, logs, shortcuts, translation and accessibility.
5. **Cloud and release:** Consent-based viewing, managed policies, private source/public reviewed binaries, verified online installer and security testing.

## Test policy
- Every implemented feature needs meaningful unit tests where applicable, integration tests, manual Windows/Linux checks, negative/security tests and regression tests for existing profile data.
- Separate statuses: specified, implemented, CI built, functionally tested, security reviewed, and released. Never mark a feature complete solely due to compilation or PyInstaller artifact creation.
- Keep existing local user data and profiles when updating builds; do not overwrite saved credentials or cookies without an explicit migration.
- Fingerprint protection has Standard, Balanced (default), Strict and Custom modes; no undetectability or website-security bypass claims.
- Themes: Dark, Light, Auto; approved cosmic neon design with shooting stars and reduced-motion.
- Default browser automatic update remains OFF; a Git push never triggers installation.
- Preserve master login, separate admin authorization, single-use emergency token, session durations/timezone windows, remote cloud management architecture, and encrypted site-specific session transfer.
- No AI Assistant. Android remains on hold. All repository documentation and UI text must be English.

## Next measurable milestone
Build a reproducible GUI runtime smoke-test workflow and a functional profile backup/restore slice, with CI checks and documented recovery. Do not merge or release failed tests.
