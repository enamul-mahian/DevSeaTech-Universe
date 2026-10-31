import type { Metadata } from "next";
import { Card, CardContent, Badge, Button } from "@devseatech/ui";
import { formatPrice } from "@devseatech/contracts";

export const metadata: Metadata = { title: "Plans" };

const PLACEHOLDER_PLANS = [
  {
    slug: "trial-24h",
    name: "Trial (24h)",
    priceMinor: 0,
    currency: "USD" as const,
    hours: 24,
    public: true,
  },
  {
    slug: "trial-72h",
    name: "Trial (72h)",
    priceMinor: 0,
    currency: "USD" as const,
    hours: 72,
    public: true,
  },
  {
    slug: "standard-30d",
    name: "Standard",
    priceMinor: 1500,
    currency: "USD" as const,
    hours: 720,
    public: true,
  },
  {
    slug: "team-30d",
    name: "Team",
    priceMinor: 0,
    currency: "USD" as const,
    hours: 720,
    public: false,
  },
];

export default function PlansPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Plans</h1>
          <p className="mt-1 text-muted-foreground">
            Pricing plans. Final price is always calculated server-side.
          </p>
        </div>
        <Button size="sm">Create Plan</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {PLACEHOLDER_PLANS.map((p) => (
          <Card key={p.slug}>
            <CardContent className="flex flex-col gap-3 pt-6">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{p.name}</h2>
                <Badge tone={p.public ? "accent" : "neutral"}>
                  {p.public ? "Public" : "Private"}
                </Badge>
              </div>
              <p className="text-2xl font-bold">
                {p.priceMinor === 0
                  ? "Free"
                  : formatPrice(p.priceMinor, p.currency)}
              </p>
              <p className="text-sm text-muted-foreground">
                {p.hours}h entitlement · {p.currency}
              </p>
              <Button variant="secondary" size="sm">
                Edit
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="text-xs text-muted-foreground">
        Placeholder data. Live plans are managed through the API. Do not enable
        real charges without explicit authorization.
      </p>
    </div>
  );
}
