# Release Distribution and Update Policy (Decision v1.8)

Status: Product decision approved. Update delivery is not implemented.

## Distribution
- Keep `enamul-mahian/DevSeaTech-Universe` source code private.
- Make **only reviewed, signed installer binaries and required public notices** publicly downloadable.
- Prefer a separate public binary-distribution repository or trusted release asset host. Do not publish source, credentials, signing keys, private manifests, or sensitive artifacts.
- During development, no domain or hosted DevSeaTech update server is assumed.
- Target online bootstrapper size is 1–5 MB (a goal, not a measured build).
- The installer UI shows DevSeaTech branding rather than the source repository URL. Technical network visibility and open-source attribution must not be suppressed.

## Update semantics
- Automatic update installation is **OFF by default** for every new installation and profile.
- A Git push, merge, CI build, or branch commit **never** authorizes automatic client updates.
- The DevSeaTech release administrator must explicitly approve/publish a signed release before any client can even discover it as a valid update.
- With the user preference OFF, the browser must **not automatically download or install** an update. User-requested "Check for Updates" and explicit installation may be offered.
- With the user preference ON, the browser may install only published, approved, compatible, verified releases under the administrator policy.
- Changing update preferences is a browser settings change and **requires local administrator authentication**.
- Changes to update settings from future cloud management require authenticated, authorized, signed policies with clear precedence; no silent override of the default-off state.
- Browser application, Chromium engine runtime and extensions must have distinct update channels and policies. Do not silently replace a user's selected engine.
- Emergency security advisories may display warnings or block a demonstrably unsafe runtime; they do not imply silent installation when automatic updates are off.
- Verify signed release manifests, file hashes, platform/architecture compatibility, release channel, anti-rollback rules and trusted publisher identity before installation.
- Protect profile data and provide safe migration/rollback where compatible.

## Acceptance tests
1. Fresh install: automatic update setting is false.
2. Source commit only: no client auto-update.
3. Unpublished CI artifact: never eligible.
4. Published, signed release while user setting is off: no automatic download/install.
5. Published release while authorized setting is on: update eligible after validation.
6. Invalid signature, hash, or downgrade: update rejected.
7. Unauthorized update preference change: rejected.
8. Previously installed engine and isolated profile data preserved across supported updates.

## Outstanding design choices
Exact security-advisory delivery, background version-check policy, public binary repository name, signing infrastructure, and update cadence will be decided before production release.

## Non-goals
No AI assistant. Android remains on hold. No production installer or updater exists yet.
