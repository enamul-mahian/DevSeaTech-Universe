import type { Metadata } from "next";
import { Card, Badge, Button } from "@devseatech/ui";

export const metadata: Metadata = { title: "Customers" };

const PLACEHOLDER_CUSTOMERS = [
  { id: "cust-001", name: "Acme Corp", devices: 3, licenses: 3, status: "active" },
  { id: "cust-002", name: "Beta Labs", devices: 1, licenses: 1, status: "active" },
  { id: "cust-003", name: "Demo User", devices: 0, licenses: 0, status: "inactive" },
];

export default function CustomersPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Customers</h1>
          <p className="mt-1 text-muted-foreground">
            Customer accounts and their device/license usage.
          </p>
        </div>
        <Button size="sm">Add Customer</Button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 text-left text-muted-foreground">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Devices</th>
                <th className="px-4 py-3 font-medium">Licenses</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium" />
              </tr>
            </thead>
            <tbody>
              {PLACEHOLDER_CUSTOMERS.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-white/5 hover:bg-white/5"
                >
                  <td className="px-4 py-3 font-medium">{c.name}</td>
                  <td className="px-4 py-3">{c.devices}</td>
                  <td className="px-4 py-3">{c.licenses}</td>
                  <td className="px-4 py-3">
                    <Badge tone={c.status === "active" ? "accent" : "neutral"}>
                      {c.status}
                    </Badge>
                  </td>
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
        Placeholder data for layout. Live data requires API connection.
      </p>
    </div>
  );
}
