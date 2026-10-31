import type { Metadata } from "next";
import { Card, Badge, Button } from "@devseatech/ui";
import { STANDARD_LICENSE_HOURS } from "@devseatech/contracts";

export const metadata: Metadata = { title: "My Licenses" };

const STATUS_TONE: Record<string, "accent" | "neutral" | "success" | "danger" | "warning"> = {
  activated: "accent",
  issued: "neutral",
  expired: "danger",
  revoked: "danger",
  suspended: "warning",
};

const PLACEHOLDER_LICENSES = [
  {
    id: "lic-001",
    kind: "standard" as const,
    status: "activated" as const,
    durationHours: STANDARD_LICENSE_HOURS,
    activatedAt: "2026-10-01T12:00:00Z",
    expiresAt: "2026-10-31T12:00:00Z",
    deviceLabel: "WIN-OFFICE-01",
  },
  {
    id: "lic-002",
    kind: "trial" as const,
    status: "expired" as const,
    durationHours: 72,
    activatedAt: "2026-09-01T00:00:00Z",
    expiresAt: "2026-09-04T00:00:00Z",
    deviceLabel: "LNX-DEV-02",
  },
];

export default function LicensesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Licenses</h1>
        <p className="mt-1 text-muted-foreground">
          View and manage your software licenses. All timing is
          server-authoritative.
        </p>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">License</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Device</th>
                <th className="px-4 py-3 font-medium">Expires</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {PLACEHOLDER_LICENSES.map((lic) => (
                <tr
                  key={lic.id}
                  className="border-b border-white/5 hover:bg-white/5"
                >
                  <td className="px-4 py-3 font-mono text-xs">{lic.id}</td>
                  <td className="px-4 py-3 capitalize">{lic.kind}</td>
                  <td className="px-4 py-3">
                    <Badge tone={STATUS_TONE[lic.status] ?? "neutral"}>
                      {lic.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {lic.deviceLabel}
                  </td>
                  <td className="px-4 py-3">
                    {lic.expiresAt
                      ? new Date(lic.expiresAt).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="sm">
                      Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 className="font-semibold">Activate a License</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Enter your license key to activate on this device. Activation is
          server-confirmed — a browser success redirect never activates a
          license.
        </p>
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            placeholder="Enter license key"
            className="flex-1 rounded-md border border-white/20 bg-white/5 px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-accent focus:outline-none"
            disabled
          />
          <Button size="sm" disabled>
            Activate
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Activation requires API connection. Placeholder for layout.
        </p>
      </div>
    </div>
  );
}
