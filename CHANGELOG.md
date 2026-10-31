# Changelog

All notable changes to DevSeaTech Browser are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-10-31

First internal release. Desktop browser proof of concept with all 18
approved features implemented, tested, and security-reviewed.

### Added

- **Core browser** — Qt WebEngine tabbed browser with address bar,
  per-profile isolated storage, scrypt master/admin authentication,
  session timer, and branded neon login UI.
- **AF-01 Crash Recovery & Session Restore** — automatic session saving,
  crash detection, and tab restoration on relaunch.
- **AF-02 Automatic Local Profile Backup** — encrypted (Fernet + scrypt)
  profile backups with scheduled or manual trigger.
- **AF-03 Profile Health Check** — detects corrupt, oversized, or
  missing profile data and reports actionable findings.
- **AF-04 Engine Compatibility Checker** — validates Qt WebEngine
  runtime, Python version, and OS compatibility.
- **AF-05 Download Manager** — tracks downloads with progress,
  completion, cancellation; blocks risky extensions and path traversal.
- **AF-06 Secure Password Vault** — AES-encrypted per-profile credential
  store with master-key unlock; locked vault denies all reads.
- **AF-07 Profile Import/Export/Clone** — encrypted archive round-trip
  with passphrase protection; blocked fields (passwords, vault,
  auth_tokens) excluded from templates.
- **AF-08 Proxy Health Monitor** — proxy URL parsing and config
  validation; rejects invalid ports and malformed URLs.
- **AF-09 Resource Manager** — memory/CPU snapshot collection, policy
  evaluation, and violation reporting.
- **AF-10 License Renewal Reminder** — server-authoritative epoch-based
  license timing (720 h standard, 24/72 h trial); renewal alerts.
- **AF-11 Profile Templates** — CRUD for profile templates with
  sensitive-field blocking.
- **AF-12 Permission Manager** — site permission workflow with
  default = ASK (never ALLOW).
- **AF-13 Security & Activity Logs** — append-only JSONL audit log with
  password redaction and structured query.
- **AF-14 Browser Diagnostics & Repair** — read-only system checks
  (disk, memory, profile integrity) with repair suggestions.
- **AF-15 Workspace & Group Management** — create, search, and manage
  named workspaces with profile assignment.
- **AF-16 Keyboard Shortcuts Manager** — customizable shortcuts with
  conflict detection and validation.
- **AF-17 Website Translation** — per-site translation config with
  privacy disclosure requirement when enabled.
- **AF-18 Accessibility Settings** — font scaling, high contrast, and
  preset management with bounds validation.
- **Browser Home Page** — speed-dial home page with XSS-safe HTML
  generation.
- **Profile Dashboard** — sidebar-nav profile manager with search,
  selection gating, and symlink/special-char rejection.
- **GUI smoke harness** — offscreen Qt WebEngine test for CI on
  Linux/Windows.

### Testing

- 270 tests total, all passing.
  - 221 unit tests covering every feature module.
  - 24 runtime integration tests exercising end-to-end workflows.
  - 25 security review tests (encryption, XSS, path traversal,
    input validation, permission defaults, credential handling).

### Security notes

- Vault data encrypted at rest; locked vault denies all credential reads.
- Profile exports are encrypted; tampered backups are detected.
- Default permission is ASK, never ALLOW.
- Passwords redacted in audit logs; logs are append-only.
- Home page speed-dial HTML-escapes all user input.
- Profile listing rejects symlinks and special characters.
- License timing is epoch-based and server-authoritative.

### Known limitations

- OS keystore integration not yet wired (passphrase supplied by caller).
- Login UI does not yet match final reference image (deferred).
- No production installer, signed binaries, or update server.
- Web platform scaffold exists but is not build-verified.
- Source repository is currently public; brief requires private.
- No deployment, no live payments, no production release.
