# Online Installer and Release Distribution Architecture

Status: Approved architecture decision; implementation pending.

## Decisions
- Interim distribution: GitHub-backed releases for the private `enamul-mahian/DevSeaTech-Universe` repository.
- Future distribution: official DevSeaTech domain with GitHub or private artifact storage behind the service.
- Bootstrapper target: 1–5 MB **goal, not a guarantee**; actual size must be measured.
- Do not display the GitHub repository name in the normal installation interface.
- Keep publisher information, required open-source licence notices, security diagnostics, and source attribution accessible where legally required.
- No DevSeaTech domain has yet been purchased or hosted; do not assume an operating update service.
- Browser updates must preserve installed profiles, cookies, cache, session policy and version selection unless a documented migration requires user approval.

## Interim delivery architecture
1. CI builds and tests the browser packages for Windows/Linux.
2. A release pipeline publishes signed assets and a signed version manifest.
3. A lightweight bootstrapper contacts a configured distribution endpoint over HTTPS.
4. During the interim stage, authorized downloads use GitHub-hosted release assets, with no long-lived GitHub token embedded in the client.
5. Downloads are validated against an independently trusted signing key, integrity hashes, expected platform, architecture and release channel.
6. Install the core, a default verified Chromium runtime, and dependencies. Additional Chromium runtimes are optional downloads.
7. Support download retry/resume where possible, transaction-safe installs, explicit disk requirements and rollback.
8. Do not present a successful installation until launch checks and runtime verification pass.

## Critical private repository constraint
Private GitHub release assets cannot be fetched anonymously. Never put a personal access token, GitHub App private key, or shared long-lived secret in the publicly distributed installer. Interim choices:
- Publish only audited, non-sensitive release binaries to a public release distribution repository or artifact host while keeping source private; or
- Use a trusted authenticated delivery gateway to issue short-lived scoped downloads; or
- Require operator/user GitHub authorization during installation if the product is internal only.

The installer must never claim that making its UI omit a URL conceals the network endpoint from security tools.

## Future domain migration
Introduce a configuration-controlled distribution endpoint so the download backend may move to an official DevSeaTech HTTPS domain without changing browser profile data or authentication policy. Migrate only with authenticated signed configuration. No hardcoded purchased domain dependency should be introduced before ownership and hosting are confirmed.

## Release gates
- Supply-chain threat model and signed manifest verification
- Provenance and hash validation
- Windows publisher signing and Linux package verification
- Offline/error behavior; proxy/network handling
- Engine compatibility testing and sandbox verification
- Size, startup and disk-use benchmarks
- Rollback and interrupted-download tests
- Private-source licensing and third-party notices audit

## Project constraints retained
No AI assistant. Android remains on hold. Cloud management and consent-based remote viewing remain future work. Master/admin login, timers, per-profile isolation, encrypted session transfer and proxy support remain required.

## Current implementation status
Design/documentation only. There is no downloadable installer, published release artifact, hosted DevSeaTech update endpoint, or production deployment yet.
