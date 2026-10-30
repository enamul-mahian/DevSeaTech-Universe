import { z } from "zod";

/**
 * Pricing plan. Prices are integer minor units (e.g. cents / poisha) to avoid
 * floating-point money. Final price is always calculated server-side; the
 * client never submits a trusted amount.
 */
export const Plan = z.object({
  id: z.string().uuid(),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  name: z.string().min(1),
  description: z.string().default(""),
  /** Price in minor currency units. */
  priceMinor: z.number().int().nonnegative(),
  currency: z.enum(["USD", "BDT"]),
  /** Entitlement granted by this plan, in hours. */
  durationHours: z.number().int().positive(),
  isPublic: z.boolean().default(true),
  features: z.array(z.string()).default([]),
});
export type Plan = z.infer<typeof Plan>;

/** Format a minor-unit amount for display. */
export function formatPrice(priceMinor: number, currency: Plan["currency"]): string {
  const major = priceMinor / 100;
  const symbol = currency === "USD" ? "$" : "৳";
  return `${symbol}${major.toLocaleString(undefined, {
    minimumFractionDigits: major % 1 === 0 ? 0 : 2,
    maximumFractionDigits: 2,
  })}`;
}
