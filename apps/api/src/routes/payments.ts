import { Hono } from "hono";
import {
  ok,
  fail,
  CreateCheckoutRequest,
  type PaymentIntent,
  type WebhookEvent,
} from "@devseatech/contracts";

/**
 * Payment routes. All payment flows default to SANDBOX/TEST mode.
 * Real charges are NOT enabled until the owner explicitly authorizes go-live.
 *
 * Gateway credentials MUST be in encrypted environment/secret storage.
 * Never put credentials in client-side code or commit them to the repo.
 *
 * CRITICAL: A browser success redirect NEVER activates a license.
 * Only a verified webhook with a valid signature triggers activation.
 */

const IS_LIVE = process.env.PAYMENT_LIVE === "true";

const paymentStore = new Map<string, PaymentIntent>();
const webhookLog: WebhookEvent[] = [];

// Seed a demo payment for dev/test.
paymentStore.set("00000000-0000-0000-0000-p00000000001", {
  id: "00000000-0000-0000-0000-p00000000001",
  customerId: "00000000-0000-0000-0000-c00000000001",
  planSlug: "standard-30d",
  amountMinor: 1500,
  currency: "USD",
  gateway: "stripe",
  status: "succeeded",
  gatewayRef: "pi_test_demo_001",
  isLive: false,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
});

export const paymentRoutes = new Hono();

// List payments for the authenticated customer (placeholder: returns all).
paymentRoutes.get("/", (c) => {
  return c.json(ok(Array.from(paymentStore.values())));
});

// Get a single payment.
paymentRoutes.get("/:id", (c) => {
  const payment = paymentStore.get(c.req.param("id"));
  if (!payment) return c.json(fail("not_found", "Payment not found"), 404);
  return c.json(ok(payment));
});

/**
 * Create a checkout session. The server calculates the final amount from
 * the plan — the client never submits a trusted price.
 */
paymentRoutes.post("/checkout", async (c) => {
  const parsed = CreateCheckoutRequest.safeParse(await c.req.json());
  if (!parsed.success) {
    return c.json(fail("validation", parsed.error.message), 400);
  }

  const { planSlug, gateway, successUrl, cancelUrl } = parsed.data;

  // In production: look up plan, calculate price server-side, create
  // a real Stripe/SSLCommerz session. Here we return a test session.
  const paymentId = crypto.randomUUID();
  const now = new Date().toISOString();

  const intent: PaymentIntent = {
    id: paymentId,
    customerId: "00000000-0000-0000-0000-c00000000001", // placeholder
    planSlug,
    amountMinor: 1500, // server-calculated from plan
    currency: "USD",
    gateway,
    status: "pending",
    gatewayRef: null,
    isLive: IS_LIVE,
    createdAt: now,
    updatedAt: now,
  };
  paymentStore.set(paymentId, intent);

  // In production: create a real checkout session with the gateway SDK.
  // The checkoutUrl would come from Stripe/SSLCommerz.
  const checkoutUrl = gateway === "stripe"
    ? `https://checkout.stripe.com/test/${paymentId}`
    : `https://sandbox.sslcommerz.com/test/${paymentId}`;

  return c.json(ok({
    paymentIntentId: paymentId,
    checkoutUrl,
    gateway,
    isLive: IS_LIVE,
  }));
});

/**
 * Webhook endpoint for payment gateways. In production:
 * 1. Verify the webhook signature using the gateway's signing secret
 * 2. Only trust verified webhooks
 * 3. On successful payment: activate the associated license (server-side only)
 * 4. A browser redirect to successUrl NEVER activates a license
 */
paymentRoutes.post("/webhook/:gateway", async (c) => {
  const gateway = c.req.param("gateway");
  if (gateway !== "stripe" && gateway !== "sslcommerz") {
    return c.json(fail("invalid_gateway", "Unknown payment gateway"), 400);
  }

  let payload: Record<string, unknown>;
  try {
    payload = await c.req.json() as Record<string, unknown>;
  } catch {
    return c.json(fail("invalid_payload", "Invalid JSON payload"), 400);
  }

  // In production: verify the webhook signature from the request headers.
  // Stripe: stripe.webhooks.constructEvent(body, sig, endpointSecret)
  // SSLCommerz: verify IPN hash with store credentials
  const verified = false; // NEVER trust without verification

  const event: WebhookEvent = {
    id: crypto.randomUUID(),
    gateway,
    eventType: String(payload["type"] ?? payload["tran_id"] ?? "unknown"),
    payload,
    verified,
    receivedAt: new Date().toISOString(),
  };
  webhookLog.push(event);

  if (!verified) {
    // Log but do not act on unverified webhooks.
    console.warn(`Unverified webhook from ${gateway}: ${event.id}`);
    return c.json(ok({ received: true, verified: false }));
  }

  // In production with a verified webhook:
  // - Look up the payment intent by gateway reference
  // - Update payment status to "succeeded"
  // - Activate the associated license (server-authoritative timing)
  // - Never activate based on a browser redirect

  return c.json(ok({ received: true, verified: true }));
});

// List webhook events (admin only in production).
paymentRoutes.get("/webhooks/log", (c) => {
  return c.json(ok(webhookLog));
});
