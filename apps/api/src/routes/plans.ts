import { Hono } from "hono";
import { ok, fail, type Plan, STANDARD_LICENSE_HOURS } from "@devseatech/contracts";

/**
 * In-memory plan store. Production replaces this with a database.
 * Final price is always calculated server-side — the client never submits a
 * trusted amount.
 */
const store = new Map<string, Plan>();

// Seed default plans.
const defaults: Plan[] = [
  {
    id: "00000000-0000-0000-0000-p00000000001",
    slug: "trial-24h",
    name: "Trial (24h)",
    description: "24-hour trial on a single device.",
    priceMinor: 0,
    currency: "USD",
    durationHours: 24,
    isPublic: true,
    features: ["24 hours", "Single device", "Core profiles"],
  },
  {
    id: "00000000-0000-0000-0000-p00000000002",
    slug: "trial-72h",
    name: "Trial (72h)",
    description: "72-hour trial on a single device.",
    priceMinor: 0,
    currency: "USD",
    durationHours: 72,
    isPublic: true,
    features: ["72 hours", "Single device", "Core profiles"],
  },
  {
    id: "00000000-0000-0000-0000-p00000000003",
    slug: "standard-30d",
    name: "Standard",
    description: "30-day (720h) license per device.",
    priceMinor: 1500,
    currency: "USD",
    durationHours: STANDARD_LICENSE_HOURS,
    isPublic: true,
    features: [
      "30 days (720h) per device",
      "All privacy modes",
      "Proxy + engine management",
      "Priority support",
    ],
  },
];
for (const p of defaults) store.set(p.id, p);

export const planRoutes = new Hono();

// List public plans (or all for admin).
planRoutes.get("/", (c) => {
  const showAll = c.req.query("all") === "true";
  const plans = Array.from(store.values()).filter(
    (p) => showAll || p.isPublic,
  );
  return c.json(ok(plans));
});

// Get one plan.
planRoutes.get("/:id", (c) => {
  const plan = store.get(c.req.param("id"));
  if (!plan) return c.json(fail("not_found", "Plan not found"), 404);
  return c.json(ok(plan));
});
