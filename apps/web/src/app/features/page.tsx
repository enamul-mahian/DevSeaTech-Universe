import type { Metadata } from "next";
import { Card, CardContent } from "@devseatech/ui";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Features" };

const FEATURE_GROUPS = [
  {
    title: "Multi-Profile System",
    features: [
      "Isolated cookies, cache, storage, and history per profile",
      "One master login unlocks all profiles",
      "Profile health checks and automated backup",
      "Import, export, and clone profiles with encrypted archives",
      "Profile templates with sensitive-field blocking",
    ],
  },
  {
    title: "Security & Privacy",
    features: [
      "Encrypted password vault with master-key unlock",
      "Append-only security audit logs with password redaction",
      "Permission manager (default = ASK, never ALLOW)",
      "XSS-safe HTML generation for home page and dashboard",
      "Path traversal and risky extension blocking in downloads",
    ],
  },
  {
    title: "Engine & Proxy Management",
    features: [
      "Qt WebEngine runtime compatibility checking",
      "HTTP, HTTPS, and SOCKS5 proxy configuration per profile",
      "Proxy health monitoring and validation",
      "Resource usage monitoring with policy-based alerts",
    ],
  },
  {
    title: "Licensing & Administration",
    features: [
      "Server-authoritative license timing (720h standard, 24/72h trial)",
      "Device enrollment with cryptographic identity",
      "License renewal reminders and expiration alerts",
      "Role-based admin controls with audit trails",
    ],
  },
  {
    title: "Productivity & Accessibility",
    features: [
      "Workspace and profile group management",
      "Customizable keyboard shortcuts with conflict detection",
      "Website translation with privacy disclosure",
      "Accessibility settings: font scaling, high contrast, presets",
      "Browser diagnostics and repair tools",
    ],
  },
  {
    title: "Reliability",
    features: [
      "Crash recovery and automatic session restore",
      "Download manager with progress tracking",
      "Fail-closed auto-update policy (OFF by default)",
      "GUI smoke testing on Linux and Windows",
    ],
  },
];

export default function FeaturesPage() {
  return (
    <PageShell
      title="Features"
      intro="DevSeaTech Universe includes 18 verified features for secure, managed browsing. Every capability is tested, security-reviewed, and auditable."
    >
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURE_GROUPS.map((group) => (
          <Card key={group.title}>
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold">{group.title}</h2>
              <ul className="mt-3 space-y-2">
                {group.features.map((f) => (
                  <li
                    key={f}
                    className="flex gap-2 text-sm text-muted-foreground"
                  >
                    <span className="text-accent" aria-hidden>
                      ✓
                    </span>
                    {f}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </PageShell>
  );
}
