# Monthly Device License and Binding Architecture — v1.9

Status: Approved feature direction. **Design and security review only; no production implementation.**

## Confirmed product requirements

- One license authorizes one registered Windows/Linux device.
- The active license lasts one month.
- Bind a license to a device identifier and its recorded MAC address; do not treat the public IP as an enforcement identifier.
- IP address is collected only as a contextual monitoring signal, subject to privacy controls.
- Administrators may release a device binding, revoke a license, issue a replacement license, or permanently suspend a device from the cloud management panel.
- A suspended device cannot acquire a replacement license without an explicit privileged administrative reversal.
- No profile, cookie, cache, bookmark, password, or saved session is erased merely because a license expires, is revoked, or is suspended.
- Master login, administrator authentication, existing timezone and session-timer policies, and one-time emergency access tokens remain separate controls. Emergency access does not silently bypass license suspension or expiry.
- User-facing messages, admin dashboard, source code, and documentation remain English only.
- Android remains on hold; no AI assistant.

## Provisional time semantics (requires product sign-off)

Define one month as one **calendar month** from server-confirmed activation time, in UTC. Example: January 15 10:00 UTC to February 15 10:00 UTC. For a day absent in the next month, clamp to the final day of the next month. Do not implement this definition until confirmed. Renewal timing, grace period, refund policy and offline activation limits remain open decisions.

## Server-authoritative license lifecycle

Draft -> Issued -> Activated -> Expired
                         |-> Revoked
                         |-> Binding Released (requires reactivation)
A device can additionally have an independent permanent-suspension flag.

License data model (conceptual):
- license_id, license_key_digest, account_id, device_id
- device_public_key, key_attestation_status, recorded_mac_hashes
- activation_time_utc, expiry_time_utc, last_verified_utc
- status, suspension_reason, suspension_actor, suspension_time_utc
- binding_history, replacement_history, audit_events
- optional observed_public_ip and its short retention deadline

The signing key and private device key must not be stored in the browser package or the GitHub repository.

## Strong device-binding model

- Generate a unique device key pair during enrollment and prove possession to the server using a challenge-response protocol.
- Prefer OS-backed non-exportable key storage (Windows TPM when available; Linux protected key storage where supported).
- Treat device ID as the server-issued identifier linked to this cryptographic identity.
- MAC addresses are changeable, can be spoofed, and may be randomized or altered by NIC replacement. Treat MAC matching as a secondary consistency signal, not sole proof or unconditional ban.
- Do not deny service merely because a public IP changes or a new shared IP matches a different user.
- Require a controlled re-enrollment flow for genuine hardware replacements.
- Design for device compromise and stolen credential scenarios, including token revocation and key rotation.

## Administration and audit

Provide admin actions: Issue, Activate, Renew, Release Binding, Reissue, Revoke, Permanently Suspend, Review Device, and Explicitly Lift Suspension. Require privileged authorization, step-up MFA for destructive actions, reason codes, confirmations and tamper-resistant audit events. De-duplicate retry requests through idempotency keys.

## Offline and emergency-access policy

- Online activation and scheduled server validation are required for authoritative license status.
- Signed, time-limited offline entitlements may be supported only after defining a maximum offline interval and revocation latency.
- Server-issued one-use emergency login tokens still use the existing session timer and do not imply a valid license or revoke a device suspension.
- A true irreversible hardware ban cannot be guaranteed against OS reinstall, spoofing or hardware changes. The design guarantees a server-side suspension of the known registered device identity, not universal physical identification.

## Privacy, compliance and tests

- Explain collection of device identity, MAC signal, observed IP and retention in a privacy notice.
- Minimize/rotate IP observation, never expose full IP/MAC to unprivileged dashboard viewers, and scope access to authorized staff.
- Avoid storing raw hardware identifiers if keyed hashes or appropriately scoped encrypted fields satisfy requirements.
- Validate monthly expiry at boundary conditions, replay attacks, same license on two devices, revoked license, changed IP, MAC randomization, offline expiry, clock rollback, admin release, mistaken suspension and replacement device onboarding.
- Never rely on local system clock alone for expiry enforcement.
- Do not automatically delete browser profiles on suspension.

## Implementation gate

Before implementation: confirm the exact month-duration calculation, renewal and offline grace semantics, admin recovery rules, and IP/MAC retention period. Verify availability and behavior of hardware-backed device keys across targeted Windows and Linux editions.

## References
- https://learn.microsoft.com/windows/security/hardware-security/tpm/tpm-fundamentals
- https://www.rfc-editor.org/rfc/rfc9724.html
- https://www.ncsc.gov.uk/collection/device-security-principles-for-manufacturers/support-appropriate-authentication
