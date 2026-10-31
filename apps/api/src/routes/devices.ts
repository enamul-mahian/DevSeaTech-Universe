import { Hono } from "hono";
import { ok, fail, type Device } from "@devseatech/contracts";

/**
 * In-memory device store. Production replaces this with a database.
 * IP is recorded for monitoring only — never used for auto-blocking.
 */
const store = new Map<string, Device>();

// Seed a demo device.
store.set("00000000-0000-0000-0000-d00000000001", {
  id: "00000000-0000-0000-0000-d00000000001",
  customerId: "00000000-0000-0000-0000-c00000000001",
  deviceKeyFingerprint: "demo-fingerprint-abc123",
  label: "WIN-OFFICE-01",
  os: "windows",
  macSignals: [],
  lastSeenIp: null,
  status: "active",
  enrolledAt: new Date().toISOString(),
});

export const deviceRoutes = new Hono();

// List all devices.
deviceRoutes.get("/", (c) => {
  return c.json(ok(Array.from(store.values())));
});

// Get one device.
deviceRoutes.get("/:id", (c) => {
  const dev = store.get(c.req.param("id"));
  if (!dev) return c.json(fail("not_found", "Device not found"), 404);
  return c.json(ok(dev));
});

// Enroll a new device.
deviceRoutes.post("/", async (c) => {
  const body = await c.req.json();
  const id = crypto.randomUUID();
  const device: Device = {
    id,
    customerId: body.customerId ?? "00000000-0000-0000-0000-c00000000001",
    deviceKeyFingerprint: body.deviceKeyFingerprint ?? "",
    label: body.label ?? null,
    os: body.os ?? null,
    macSignals: body.macSignals ?? [],
    lastSeenIp: null, // server records, never client-set
    status: "active",
    enrolledAt: new Date().toISOString(),
  };
  store.set(id, device);
  return c.json(ok(device), 201);
});
