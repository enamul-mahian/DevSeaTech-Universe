import type { Metadata } from "next";
import { Badge, Button, Card, CardContent } from "@devseatech/ui";
import { formatPrice, type Plan } from "@devseatech/contracts";
import { PageShell } from "@/components/page-shell";

export const metadata: Metadata = { title: "Pricing" };

// Placeholder plans for layout. Real plans are server-managed (CMS + admin),
// and the final price is always calculated server-side at checkout.
const PLANS: (Pick<Plan, "name" | "priceMinor" | "currency" | "durationHours"> & {
  highlight?: boolean;
  features: string[];
})[] = [
  {
    name: "Trial",
    priceMinor: 0,
    currency: "USD",
    durationHours: 72,
    features: ["24h / 72h / custom hours", "Single device", "Core profiles"],
  },
  {
    name: "Standard",
    priceMinor: 1500,
    currency: "USD",
    durationHours: 720,
    highlight: true,
    features: [
      "30 days (720h) per device",
      "All privacy modes",
      "Proxy + engine management",
      "Priority support",
    ],
  },
  {
    name: "Team",
    priceMinor: 0,
    currency: "USD",
    durationHours: 720,
    features: ["Volume device licenses", "Central admin dashboard", "Custom policies"],
  },
];

export default function PricingPage() {
  return (
    <PageShell
      title="Pricing"
      intro="Simple device-based licensing. Start with a trial, then license per authorized device. Final pricing is confirmed at checkout."
    >
      <div className="grid gap-5 lg:grid-cols-3">
        {PLANS.map((plan) => (
          <Card
            key={plan.name}
            className={plan.highlight ? "neon-ring" : undefined}
          >
            <CardContent className="flex h-full flex-col gap-4 pt-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">{plan.name}</h2>
                {plan.highlight && <Badge tone="accent">Most popular</Badge>}
              </div>
              <p className="text-3xl font-bold">
                {plan.priceMinor === 0
                  ? plan.name === "Team"
                    ? "Contact us"
                    : "Free"
                  : formatPrice(plan.priceMinor, plan.currency)}
                {plan.priceMinor > 0 && (
                  <span className="text-sm font-normal text-muted-foreground">
                    {" "}
                    / device · 30 days
                  </span>
                )}
              </p>
              <ul className="flex-1 space-y-2 text-sm text-muted-foreground">
                {plan.features.map((f) => (
                  <li key={f} className="flex gap-2">
                    <span className="text-accent" aria-hidden>
                      ✓
                    </span>
                    {f}
                  </li>
                ))}
              </ul>
              <Button variant={plan.highlight ? "primary" : "secondary"}>
                {plan.name === "Team" ? "Talk to sales" : "Choose " + plan.name}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
      <p className="mt-6 text-sm text-muted-foreground">
        Prices and plans shown are placeholders for layout; live plans are
        managed in the admin dashboard and validated server-side.
      </p>
    </PageShell>
  );
}
