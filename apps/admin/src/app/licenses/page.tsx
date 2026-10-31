import type { Metadata } from "next";
import { Card, CardContent, Badge, Button } from "@devseatech/ui";
import type { LicenseStatus } from "@devseatech/contracts";

export const metadata: Metadata = { title: "Licenses" };

/**
 * Placeholder license rows. In production these are fetched from the API with
 * pagination and filtering. Final activation/expiry is always server-side.
 */
const PLACEHOLDER_LICENSES: {
  id: string;
  kind: string;
  status: LicenseStatus;
  device: string;
  expires: string;
}[] = [
  {
    id: "demo-001",
    kind: "standard",
    status: "activated",
    device: "WIN-OFFICE-01",
    expires: "2026-12-01",
  },
  {
    id: "demo-002",
    kind: "trial",
    status: "expired",
    device: "LNX-DEV-02",
    expires: "2026-10-15",
  },
  {
    id: "demo-003",
    kind: "standard",
    status: "issued",
    device: "—",
    expires: "—",
  },
];

const STATUS_TONE: Record<string, "accent" | "neutral"> = {
  activated: "accent",
  expired: "neutral",
  issued: "neutral",
  revoked: "neutral",
  suspended: "neutral",
  draft: "neutral",
};

export default function LicensesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Licenses</h1>
          <p className="mt-1 text-muted-foreground">
            Manage device licenses. Activation is server-authoritative.
          </p>
        </div>
        <Button size="sm">Issue License</Button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Kind</th>
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
                  <td className="px-4 py-3 font-mono text-xs">{lic.device}</td>
                  <td className="px-4 py-3">{lic.expires}</td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <p className="text-xs text-muted-foreground">
        Data above is placeholder for layout. Live data requires API connection.
        A browser success redirect never activates a license.
      </p>
    </div>
  );
}
