import { z } from "zod";

/**
 * License lifecycle (server-authoritative). All timestamps are ISO-8601 UTC
 * strings assigned by the server; clients never set activation or expiry time.
 */
export const LicenseStatus = z.enum([
  "draft",
  "issued",
  "activated",
  "expired",
  "revoked",
  "suspended",
]);
export type LicenseStatus = z.infer<typeof LicenseStatus>;

export const LicenseKind = z.enum(["trial", "standard"]);
export type LicenseKind = z.infer<typeof LicenseKind>;

/** Standard paid license: exactly 30 consecutive days from activation. */
export const STANDARD_LICENSE_HOURS = 720;

/** Administrator-definable trial presets (hours); admin may set any value > 0. */
export const TRIAL_PRESET_HOURS = [24, 72] as const;

export const License = z.object({
  id: z.string().uuid(),
  kind: LicenseKind,
  status: LicenseStatus,
  customerId: z.string().uuid(),
  /** Bound device, if the license has been activated on one. */
  deviceId: z.string().uuid().nullable(),
  /** Entitlement window in hours (720 for standard; admin-defined for trials). */
  durationHours: z.number().int().positive(),
  /** Server-confirmed activation time (UTC). Null until activated. */
  activatedAt: z.string().datetime().nullable(),
  /** Server-computed expiry (UTC). Null until activated. */
  expiresAt: z.string().datetime().nullable(),
  createdAt: z.string().datetime(),
});
export type License = z.infer<typeof License>;

/**
 * Compute the expiry instant from a server-confirmed activation instant.
 * Pure and UTC-based so it is identical on server and in tests. Never derive
 * expiry from a client clock.
 */
export function computeExpiry(
  activatedAtIso: string,
  durationHours: number,
): string {
  const activated = new Date(activatedAtIso);
  if (Number.isNaN(activated.getTime())) {
    throw new RangeError("Invalid activation timestamp");
  }
  if (!Number.isFinite(durationHours) || durationHours <= 0) {
    throw new RangeError("durationHours must be a positive number");
  }
  return new Date(
    activated.getTime() + durationHours * 60 * 60 * 1000,
  ).toISOString();
}

/** Whether a license is currently usable at the given server time. */
export function isActive(license: License, nowIso: string): boolean {
  if (license.status !== "activated") return false;
  if (!license.expiresAt) return false;
  return new Date(nowIso).getTime() < new Date(license.expiresAt).getTime();
}

/**
 * Signed entitlement envelope delivered to a device. The signature itself is
 * produced and verified server-side; this is only the transport shape.
 */
export const SignedEntitlement = z.object({
  licenseId: z.string().uuid(),
  deviceId: z.string().uuid(),
  status: LicenseStatus,
  expiresAt: z.string().datetime().nullable(),
  /** Monotonic counter to defend against replay of an older entitlement. */
  issueSequence: z.number().int().nonnegative(),
  /** Server issue time (UTC); clients compare against server time, not local. */
  issuedAt: z.string().datetime(),
  signature: z.string().min(1),
});
export type SignedEntitlement = z.infer<typeof SignedEntitlement>;
