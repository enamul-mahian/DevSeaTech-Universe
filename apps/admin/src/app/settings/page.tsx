import type { Metadata } from "next";
import { Card, CardContent, Button } from "@devseatech/ui";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="mt-1 text-muted-foreground">
          Platform configuration. Changes are administrator-authenticated.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="space-y-4 pt-6">
            <h2 className="font-semibold">Update Policy</h2>
            <p className="text-sm text-muted-foreground">
              Automatic update installation is OFF by default. Only published,
              signed releases are eligible. A git push or CI build never
              authorizes client updates.
            </p>
            <Button variant="secondary" size="sm" disabled>
              Configure
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 pt-6">
            <h2 className="font-semibold">Payment Gateway</h2>
            <p className="text-sm text-muted-foreground">
              Payment gateway credentials are stored in encrypted environment
              secrets. Real charges are not enabled until the owner explicitly
              authorizes go-live.
            </p>
            <Button variant="secondary" size="sm" disabled>
              Configure
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 pt-6">
            <h2 className="font-semibold">License Defaults</h2>
            <p className="text-sm text-muted-foreground">
              Standard: 30 consecutive days (720h) from server-confirmed
              activation. Trials: 24h / 72h / custom. Time is always
              server-authoritative.
            </p>
            <Button variant="secondary" size="sm" disabled>
              Configure
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 pt-6">
            <h2 className="font-semibold">Security & Audit</h2>
            <p className="text-sm text-muted-foreground">
              Audit logs, session management, and security policies. All
              configuration changes require administrator authentication.
            </p>
            <Button variant="secondary" size="sm" disabled>
              Configure
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
