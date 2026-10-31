import { z } from "zod";

/**
 * Payment integration schemas. Gateway credentials MUST be stored in
 * encrypted environment/secret storage — never hardcoded or in client code.
 *
 * IMPORTANT: Do not enable real charges until the owner explicitly
 * authorizes go-live. All payment flows default to sandbox/test mode.
 */

export const PaymentGateway = z.enum(["stripe", "sslcommerz"]);
export type PaymentGateway = z.infer<typeof PaymentGateway>;

export const PaymentStatus = z.enum([
  "pending",
  "processing",
  "succeeded",
  "failed",
  "refunded",
  "cancelled",
]);
export type PaymentStatus = z.infer<typeof PaymentStatus>;

export const PaymentIntent = z.object({
  id: z.string().uuid(),
  customerId: z.string().uuid(),
  planSlug: z.string(),
  /** Amount in minor currency units (cents / poisha). */
  amountMinor: z.number().int().nonnegative(),
  currency: z.enum(["USD", "BDT"]),
  gateway: PaymentGateway,
  status: PaymentStatus,
  /** Gateway's own transaction/session ID. Null until the gateway responds. */
  gatewayRef: z.string().nullable(),
  /**
   * Whether this is a live or test/sandbox transaction.
   * MUST be false until go-live is explicitly authorized.
   */
  isLive: z.boolean().default(false),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type PaymentIntent = z.infer<typeof PaymentIntent>;

/**
 * Webhook event from a payment gateway. The server verifies the webhook
 * signature before trusting any payload.
 */
export const WebhookEvent = z.object({
  id: z.string(),
  gateway: PaymentGateway,
  eventType: z.string(),
  /** Raw payload from the gateway, stored for audit. */
  payload: z.record(z.unknown()),
  /** Whether the webhook signature was verified. */
  verified: z.boolean(),
  receivedAt: z.string().datetime(),
});
export type WebhookEvent = z.infer<typeof WebhookEvent>;

/**
 * Create checkout session request. The server calculates the final amount
 * from the plan — the client never submits a trusted amount.
 */
export const CreateCheckoutRequest = z.object({
  planSlug: z.string().min(1),
  gateway: PaymentGateway,
  /** URL to redirect after payment success. */
  successUrl: z.string().url(),
  /** URL to redirect after payment cancellation. */
  cancelUrl: z.string().url(),
});
export type CreateCheckoutRequest = z.infer<typeof CreateCheckoutRequest>;

/**
 * Checkout session response. The client redirects to `checkoutUrl`.
 * NOTE: A browser success redirect NEVER activates a license — only a
 * verified webhook does.
 */
export const CheckoutSession = z.object({
  paymentIntentId: z.string().uuid(),
  checkoutUrl: z.string().url(),
  gateway: PaymentGateway,
  isLive: z.boolean(),
});
export type CheckoutSession = z.infer<typeof CheckoutSession>;
