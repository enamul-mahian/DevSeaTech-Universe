import { z } from "zod";

/**
 * Device identity. The cryptographic Device ID is the enforcement identifier.
 * MAC signals are recorded for binding/monitoring; public IP is a monitoring
 * signal only and must never be used as an automatic blocking identifier.
 */
export const DeviceStatus = z.enum(["active", "released", "suspended"]);
export type DeviceStatus = z.infer<typeof DeviceStatus>;

export const Device = z.object({
  id: z.string().uuid(),
  customerId: z.string().uuid(),
  /** Cryptographic device identity (public key fingerprint / enrollment id). */
  deviceKeyFingerprint: z.string().min(8),
  label: z.string().max(80).nullable(),
  os: z.enum(["windows", "linux"]).nullable(),
  /** Recorded MAC address signals (binding context, not sole proof). */
  macSignals: z.array(z.string()).default([]),
  /** Last observed public IP — monitoring only, never auto-blocking. */
  lastSeenIp: z.string().nullable(),
  status: DeviceStatus,
  enrolledAt: z.string().datetime(),
});
export type Device = z.infer<typeof Device>;
