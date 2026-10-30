import { describe, expect, it } from "vitest";
import {
  computeExpiry,
  isActive,
  License,
  STANDARD_LICENSE_HOURS,
} from "./license";

describe("computeExpiry", () => {
  it("adds exactly 720 hours (30 days) for a standard license", () => {
    const activated = "2026-01-01T00:00:00.000Z";
    expect(computeExpiry(activated, STANDARD_LICENSE_HOURS)).toBe(
      "2026-01-31T00:00:00.000Z",
    );
  });

  it("handles arbitrary trial durations", () => {
    expect(computeExpiry("2026-01-01T00:00:00.000Z", 24)).toBe(
      "2026-01-02T00:00:00.000Z",
    );
  });

  it("rejects an invalid activation timestamp", () => {
    expect(() => computeExpiry("not-a-date", 24)).toThrow(RangeError);
  });

  it("rejects a non-positive duration", () => {
    expect(() => computeExpiry("2026-01-01T00:00:00.000Z", 0)).toThrow(RangeError);
  });
});

describe("isActive", () => {
  const base = License.parse({
    id: "11111111-1111-4111-8111-111111111111",
    kind: "standard",
    status: "activated",
    customerId: "22222222-2222-4222-8222-222222222222",
    deviceId: "33333333-3333-4333-8333-333333333333",
    durationHours: STANDARD_LICENSE_HOURS,
    activatedAt: "2026-01-01T00:00:00.000Z",
    expiresAt: "2026-01-31T00:00:00.000Z",
    createdAt: "2025-12-31T00:00:00.000Z",
  });

  it("is active before expiry", () => {
    expect(isActive(base, "2026-01-15T00:00:00.000Z")).toBe(true);
  });

  it("is inactive at/after expiry", () => {
    expect(isActive(base, "2026-01-31T00:00:00.000Z")).toBe(false);
  });

  it("is inactive when suspended regardless of time", () => {
    expect(isActive({ ...base, status: "suspended" }, "2026-01-02T00:00:00.000Z")).toBe(
      false,
    );
  });
});
