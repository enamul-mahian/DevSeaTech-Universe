import type { Metadata } from "next";
import { Card, CardContent, Badge, Button } from "@devseatech/ui";
import { formatPrice } from "@devseatech/contracts";

export const metadata: Metadata = { title: "Plans" };

const PLANS = [
  {
    slug: "trial-72h",
    name: "Trial",
    priceMinor: 0,
    currency: "USD" as const,
    hours: 72,
    current: false,
    features: ["72h entitlement", "Single device", "Core profiles"],
  },
  {
    slug: "standard-30d",
    name: "Standard",
    priceMinor: 1500,
    currency: "USD" as const,
    hours: 720,
    current: true,
    features: [
      "30 days (720h) per device",
      "All privacy modes",
      "Proxy + engine management",
      "Priority support",
    ],
  },
  {
    slug: "team-30d",
    name: "Team",
    priceMinor: 0,
    currency: "USD" as const,
    hours: 720,
    current: false,
    features: [
      "Volume device licenses",
      "Central admin dashboard",
      "Custom policies",
    ],
  },
];

export default function PlansPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Plans</h1>
        <p className="mt-1 text-muted-foreground">
          View available plans. Final pricing is always calculated server-side.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PLANS.map((p) => (
          <Card
            key={p.slug}
            className={p.current ? "ring-1 ring-accent/40" : undefined}
          >
            <CardContent className="flex flex-col gap-3 pt-6">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{p.name}</h2>
                {p.current && <Badge tone="accent">Current plan</Badge>}
              </div>
              <p className="text-2xl font-bold">
                {p.priceMinor === 0
                  ? p.slug === "team-30d"
                    ? "Contact us"
                    : "Free"
                  : formatPrice(p.priceMinor, p.currency)}
              </p>
              <ul className="flex-1 space-y-1 text-sm text-muted-foreground">
                {p.features.map((f) => (
                  <li key={f} className="flex gap-2">
                    <span className="text-accent" aria-hidden>
                      ✓
                    </span>
                    {f}
                  </li>
                ))}
              </ul>
              <Button
                variant={p.current ? "ghost" : "secondary"}
                size="sm"
                disabled={p.current}
              >
                {p.current ? "Current" : "Upgrade"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="text-xs text-muted-foreground">
        Placeholder data. Live plans are managed server-side. Do not enable real
        charges without explicit authorization.
      </p>
    </div>
  );
}
