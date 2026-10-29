# Theme and Fingerprinting Privacy Architecture — v2.0

Status: Approved requirements, architecture only. **No fingerprinting protection implementation is claimed.**

## UI themes
- Dark, Light (White), and Auto (follow OS preference).
- Set Dark as an available default option, but remember an authorized user's choice.
- The approved DevSeaTech Universe look and subtle, optional shooting-star animation must adapt to each theme.
- Include reduced-motion support, high contrast, readable controls, and low-power mode.
- Theme changes are settings changes; enforce the existing administrator authorization policy.
- Interface copy, code, and GitHub documentation remain English.

## Four privacy modes
| Mode | Scope | Tradeoff |
| --- | --- | --- |
| Standard | Known tracking resource blocking, third-party cookie/storage protections subject to compatibility, permission controls and conventional WebRTC privacy safeguards | Highest compatibility |
| Balanced (**default**) | Standard plus measured fingerprinting surface reduction, consistent profile identity, permission-gated high-entropy access where feasible | Privacy and compatibility balance |
| Strict | Balanced plus more restrictive tracking and fingerprinting mitigations and tighter site permissions | Higher chance of site breakage |
| Custom | Administrator-configured per-profile controls with clearly visible per-site exceptions and an audit trail | Requires expert policy review |

These are application-specific product modes, not claims of interoperability or parity with Firefox security settings.

## Privacy controls and leak-prevention workstream
- Preserve separate cookies, cache, history, local storage, IndexedDB and session state per browser profile.
- Reduce unnecessary exposure of Canvas, WebGL, AudioContext, fonts, screen properties, Client Hints and high-entropy device APIs where the underlying engine safely supports it.
- WebRTC networking and DNS leak tests must account for direct and proxy networking, including HTTP, HTTPS and SOCKS5, IPv4/IPv6 and multiple interfaces.
- Keep Accept-Language, timezone, claimed platform and actual engine capabilities coherent; do not offer guaranteed undetectable or unique fingerprints.
- Avoid randomizing fingerprint properties on every page load. Choose stable, defensible privacy settings per profile, avoiding inconsistent spoofing.
- A per-profile setting may differ from another profile without guaranteeing uniqueness. Prefer reducing linkability over creating artificial unique fingerprints.
- Store custom settings locally by default, make sensitive changes admin-controlled, and do not upload raw fingerprint data or cookies to the management server.
- Provide clear disclosure and lawful-use controls. Do not promise bypass of website authentication, anti-fraud, rate-limiting, or access restrictions.
- For a site that breaks in Strict mode, offer a reviewable, admin-approved per-site compatibility exception instead of silently dropping protections.

## Compatibility and verification gates
1. Baseline real-world fingerprint exposure from supported Windows and Linux engines.
2. Site isolation and persistence across profiles and browser restarts.
3. Privacy modes and consistent settings after a page reload and app restart.
4. WebRTC IP, DNS and proxy leak regression tests across IPv4/IPv6 and network changes.
5. Canvas/WebGL/Audio, font, language, timezone, Client Hints and screen-property behavior across engine versions.
6. Site compatibility with sign-in, video calls, file uploads, accessibility, data-entry forms, DRM where licensed, and browser extensions.
7. GPU acceleration, performance, battery/memory usage, reduced-motion behavior.
8. Security audit before any production claim; evaluate engine support first because Qt WebEngine cannot guarantee all requested low-level mitigations.

## Confirmed existing product requirements preserved
- Windows/Linux active; Android on hold.
- No AI assistant or AI Hub in the actual product.
- Chromium 148 onward selection where compatible builds can be verified.
- Master login, separate admin credentials, session schedules and timers.
- 30-day license duration from activation, device-bound licensing with IP monitoring only.
- Auto-update off by default; approved releases only.
- Private source and public reviewed binaries.
- Optional future cloud management, consent-based remote viewing.
- No change to encrypted site-specific session import/export or existing profile data.

## References
- W3C, Mitigating Browser Fingerprinting: https://www.w3.org/TR/fingerprinting-guidance/
- Mozilla, Firefox's protection against fingerprinting: https://support.mozilla.org/en-US/kb/firefox-protection-against-fingerprinting
- Mozilla, Fingerprinting protections and compatibility tradeoffs: https://blog.mozilla.org/en/firefox/fingerprinting-protections/
