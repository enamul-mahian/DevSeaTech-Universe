import { Hono } from "hono";
import {
  ok,
  fail,
  ActivateLicenseRequest,
  computeExpiry,
  STANDARD_LICENSE_HOURS,
  type License,
} from "@devseatech/contracts";

/**
 * In-memory license store. Production replaces this with a database.
 * Timestamps are always UTC ISO-8601 set by the server — never by the client.
 */
const store = new Map<string, License>();

// Seed a demo license for dev/test.
store.set("00000000-0000-0000-0000-000000000001", {
  id: "00000000-0000-0000-0000-000000000001",
  kind: "standard",
  status: "issued",
  customerId: "00000000-0000-0000-0000-c00000000001",
  deviceId: null,
  durationHours: STANDARD_LICENSE_HOURS,
  activatedAt: null,
  expiresAt: null,
  createdAt: new Date().toISOString(),
});

export const licenseRoutes = new Hono();

// List all licenses.
licenseRoutes.get("/", (c) => {
  return c.json(ok(Array.from(store.values())));
});

// Get one license.
licenseRoutes.get("/:id", (c) => {
  const lic = store.get(c.req.param("id"));
  if (!lic) return c.json(fail("not_found", "License not found"), 404);
  return c.json(ok(lic));
});

/**
 * Activate a license on a device. The activation time and expiry are assigned
 * by the server. A browser success redirect NEVER activates a license.
 */
licenseRoutes.post("/activate", async (c) => {
  const parsed = ActivateLicenseRequest.safeParse(await c.req.json());
  if (!parsed.success) {
    return c.json(fail("validation", parsed.error.message), 400);
  }

  const { licenseKey, deviceKeyFingerprint, nonce } = parsed.data;

  // In production: look up by key, verify device enrollment, verify no
  // replay, then activate. Here we use the first issued license for demo.
  let target: License | undefined;
  for (const lic of store.values()) {
    if (lic.status === "issued") {
      target = lic;
      break;
    }
  }

  if (!target) {
    return c.json(fail("no_eligible", "No eligible license found"), 404);
  }

  const now = new Date().toISOString();
  const activated: License = {
    ...target,
    status: "activated",
    deviceId: "00000000-0000-0000-0000-d00000000001", // demo device
    activatedAt: now,
    expiresAt: computeExpiry(now, target.durationHours),
  };
  store.set(activated.id, activated);

  return c.json(ok({ license: activated, nonce }));
});
