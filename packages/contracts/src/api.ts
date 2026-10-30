import { z } from "zod";

/** Standard success/error envelope for every API response. */
export const ApiError = z.object({
  code: z.string(),
  message: z.string(),
  details: z.record(z.unknown()).optional(),
});
export type ApiError = z.infer<typeof ApiError>;

export function ok<T>(data: T): { ok: true; data: T } {
  return { ok: true, data };
}

export function fail(code: string, message: string): {
  ok: false;
  error: ApiError;
} {
  return { ok: false, error: { code, message } };
}

/** Health/readiness payload exposed by the API service. */
export const HealthStatus = z.object({
  service: z.string(),
  status: z.enum(["ok", "degraded", "down"]),
  version: z.string(),
  time: z.string().datetime(),
});
export type HealthStatus = z.infer<typeof HealthStatus>;

/**
 * License activation request. The server verifies device enrollment, assigns
 * the authoritative activation time, and returns a signed entitlement. A
 * browser success redirect never activates anything.
 */
export const ActivateLicenseRequest = z.object({
  licenseKey: z.string().min(8),
  deviceKeyFingerprint: z.string().min(8),
  /** Client-reported nonce echoed back to bind the response to this request. */
  nonce: z.string().min(8),
});
export type ActivateLicenseRequest = z.infer<typeof ActivateLicenseRequest>;
