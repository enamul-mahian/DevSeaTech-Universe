import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import {
  ok,
  fail,
  type HealthStatus,
} from "@devseatech/contracts";
import { licenseRoutes } from "./routes/licenses.js";
import { deviceRoutes } from "./routes/devices.js";
import { planRoutes } from "./routes/plans.js";
import { paymentRoutes } from "./routes/payments.js";

export const app = new Hono();

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------
app.use("*", logger());
app.use(
  "*",
  cors({
    origin: [
      "http://localhost:3000",
      "http://localhost:3001",
      "http://localhost:3002",
      process.env.WEB_ORIGIN ?? "",
      process.env.ADMIN_ORIGIN ?? "",
      process.env.PORTAL_ORIGIN ?? "",
    ].filter(Boolean),
    allowMethods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  }),
);

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------
app.get("/health", (c) => {
  const body: HealthStatus = {
    service: "devseatech-api",
    status: "ok",
    version: "0.1.0",
    time: new Date().toISOString(),
  };
  return c.json(ok(body));
});

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------
app.route("/api/licenses", licenseRoutes);
app.route("/api/devices", deviceRoutes);
app.route("/api/plans", planRoutes);
app.route("/api/payments", paymentRoutes);

// ---------------------------------------------------------------------------
// 404
// ---------------------------------------------------------------------------
app.notFound((c) => c.json(fail("not_found", "Resource not found"), 404));
