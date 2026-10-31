import type { Metadata } from "next";
import { Card, CardContent, Button } from "@devseatech/ui";

export const metadata: Metadata = { title: "Account" };

export default function AccountPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Account Settings</h1>
        <p className="mt-1 text-muted-foreground">
          Manage your profile and security preferences.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Profile</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Email</span>
                <span>user@example.com</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Customer ID</span>
                <span className="font-mono text-xs">cust-001</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Member since</span>
                <span>September 2026</span>
              </div>
            </div>
            <Button variant="secondary" size="sm" disabled>
              Edit Profile
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Security</h2>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>Password last changed: 30 days ago</p>
              <p>Two-factor authentication: Not enabled</p>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" disabled>
                Change Password
              </Button>
              <Button variant="secondary" size="sm" disabled>
                Enable 2FA
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Payment Methods</h2>
            <p className="text-sm text-muted-foreground">
              No payment methods on file. Add a payment method to purchase or
              renew licenses.
            </p>
            <Button variant="secondary" size="sm" disabled>
              Add Payment Method
            </Button>
            <p className="text-xs text-muted-foreground">
              Payment credentials are stored by the payment provider, never in
              our database. Real charges are not enabled without explicit
              authorization.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex flex-col gap-3 pt-6">
            <h2 className="font-semibold">Billing History</h2>
            <p className="text-sm text-muted-foreground">
              No transactions yet.
            </p>
            <Button variant="ghost" size="sm" disabled>
              View All Transactions
            </Button>
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
