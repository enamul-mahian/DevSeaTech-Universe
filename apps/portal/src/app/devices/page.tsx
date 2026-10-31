import type { Metadata } from "next";
import { Card, Badge, Button } from "@devseatech/ui";

export const metadata: Metadata = { title: "My Devices" };

const PLACEHOLDER_DEVICES = [
  {
    id: "dev-001",
    label: "WIN-OFFICE-01",
    os: "windows",
    status: "active" as const,
    enrolled: "2026-09-15",
  },
  {
    id: "dev-002",
    label: "LNX-DEV-02",
    os: "linux",
    status: "active" as const,
    enrolled: "2026-10-01",
  },
];

export default function DevicesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Devices</h1>
        <p className="mt-1 text-muted-foreground">
          View enrolled devices. IP is recorded for monitoring only, never
          auto-blocking.
        </p>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">Device</th>
                <th className="px-4 py-3 font-medium">OS</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Enrolled</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {PLACEHOLDER_DEVICES.map((d) => (
                <tr
                  key={d.id}
                  className="border-b border-white/5 hover:bg-white/5"
                >
                  <td className="px-4 py-3 font-mono text-xs">{d.label}</td>
                  <td className="px-4 py-3 capitalize">{d.os}</td>
                  <td className="px-4 py-3">
                    <Badge tone={d.status === "active" ? "accent" : "neutral"}>
                      {d.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">{d.enrolled}</td>
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
        <h2 className="font-semibold">Enroll a New Device</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Download and run DevSeaTech Universe on your device. The browser
          generates a cryptographic device key during first launch — enrollment
          happens automatically through the API.
        </p>
        <Button variant="secondary" size="sm" className="mt-3" disabled>
          Download Browser
        </Button>
      </div>
    </div>
  );
}
