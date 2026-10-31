import { Card, CardContent, StatCard } from "@devseatech/ui";

/** Placeholder stats — in production, fetched from the API. */
const STATS = [
  { label: "Active Licenses", value: "—", delta: "" },
  { label: "Enrolled Devices", value: "—", delta: "" },
  { label: "Expiring (7d)", value: "—", delta: "" },
  { label: "Revenue (30d)", value: "—", delta: "" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Overview of licenses, devices, and revenue.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((s) => (
          <StatCard key={s.label} label={s.label} value={s.value} />
        ))}
      </div>

      {/* Quick views */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="pt-6">
            <h2 className="font-semibold">Recent License Activity</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              License issuance, activations, and expirations will appear here
              once connected to the API backend.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <h2 className="font-semibold">Device Enrollment</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Recent device enrollments and status changes will appear here
              once connected to the API backend.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
