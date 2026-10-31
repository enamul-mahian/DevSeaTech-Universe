import type { Metadata } from "next";
import { Card, CardContent, StatCard, Badge, Button } from "@devseatech/ui";

export const metadata: Metadata = { title: "Overview" };

export default function PortalOverview() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My Account</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your licenses, devices, and subscription.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Active Licenses" value="1" />
        <StatCard label="Enrolled Devices" value="2" />
        <StatCard label="Current Plan" value="Standard" />
        <StatCard label="Days Remaining" value="28" />
      </div>

      {/* Quick actions */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">License Status</h2>
            <div className="flex items-center gap-2">
              <Badge tone="accent">Active</Badge>
              <span className="text-sm text-muted-foreground">
                Expires in 28 days
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              License timing is server-authoritative. Expiry is calculated from
              server-confirmed activation, never from a local clock.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Recent Activity</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>Device WIN-OFFICE-01 last seen 2h ago</li>
              <li>License activated on Oct 1</li>
              <li>Device LNX-DEV-02 enrolled on Oct 1</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Quick Actions</h2>
            <div className="flex flex-col gap-2">
              <Button variant="secondary" size="sm">
                View License Details
              </Button>
              <Button variant="secondary" size="sm">
                Manage Devices
              </Button>
              <Button variant="secondary" size="sm">
                Upgrade Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <p className="text-xs text-muted-foreground">
        Placeholder data for layout. Live data requires API connection and
        authentication.
      </p>
    </div>
  );
}
