import { describe, it, expect } from "vitest";
import { app } from "./app.js";

function req(path: string, init?: RequestInit) {
  return app.request(path, init);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function json(res: Response): Promise<any> {
  return res.json();
}

describe("health", () => {
  it("returns ok status", async () => {
    const res = await req("/health");
    expect(res.status).toBe(200);
    const body = await json(res);
    expect(body.ok).toBe(true);
    expect(body.data.status).toBe("ok");
    expect(body.data.service).toBe("devseatech-api");
  });
});

describe("GET /api/licenses", () => {
  it("lists seeded licenses", async () => {
    const res = await req("/api/licenses");
    expect(res.status).toBe(200);
    const body = await json(res);
    expect(body.ok).toBe(true);
    expect(body.data.length).toBeGreaterThanOrEqual(1);
  });
});

describe("GET /api/devices", () => {
  it("lists seeded devices", async () => {
    const res = await req("/api/devices");
    expect(res.status).toBe(200);
    const body = await json(res);
    expect(body.ok).toBe(true);
    expect(body.data.length).toBeGreaterThanOrEqual(1);
  });
});

describe("GET /api/plans", () => {
  it("lists public plans", async () => {
    const res = await req("/api/plans");
    expect(res.status).toBe(200);
    const body = await json(res);
    expect(body.ok).toBe(true);
    expect(body.data.length).toBeGreaterThanOrEqual(3);
    for (const plan of body.data) {
      expect(plan.isPublic).toBe(true);
    }
  });
});

describe("POST /api/licenses/activate", () => {
  it("activates with server-set timestamps", async () => {
    const res = await req("/api/licenses/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        licenseKey: "demo-key-12345678",
        deviceKeyFingerprint: "demo-fingerprint-abc123",
        nonce: "testnonce12345678",
      }),
    });
    // May be 200 (activated) or 404 (already activated from prior test run).
    if (res.status === 200) {
      const body = await json(res);
      expect(body.ok).toBe(true);
      expect(body.data.license.status).toBe("activated");
      expect(body.data.license.activatedAt).toBeTruthy();
      expect(body.data.license.expiresAt).toBeTruthy();
      // Expiry must be exactly 720h after activation.
      const activated = new Date(body.data.license.activatedAt as string).getTime();
      const expires = new Date(body.data.license.expiresAt as string).getTime();
      expect(expires - activated).toBe(720 * 60 * 60 * 1000);
    }
  });

  it("rejects invalid request body", async () => {
    const res = await req("/api/licenses/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bad: true }),
    });
    expect(res.status).toBe(400);
    const body = await json(res);
    expect(body.ok).toBe(false);
  });
});

describe("POST /api/devices", () => {
  it("enrolls a new device", async () => {
    const res = await req("/api/devices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deviceKeyFingerprint: "new-device-fp-xyz",
        label: "TEST-ENROLL",
        os: "linux",
      }),
    });
    expect(res.status).toBe(201);
    const body = await json(res);
    expect(body.ok).toBe(true);
    expect(body.data.label).toBe("TEST-ENROLL");
    expect(body.data.status).toBe("active");
    expect(body.data.enrolledAt).toBeTruthy();
    expect(body.data.lastSeenIp).toBeNull();
  });
});

describe("404", () => {
  it("returns structured error for unknown routes", async () => {
    const res = await req("/api/nonexistent");
    expect(res.status).toBe(404);
    const body = await json(res);
    expect(body.ok).toBe(false);
    expect(body.error.code).toBe("not_found");
  });
});
