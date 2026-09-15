# Stage 5C — Billing & Payment Integration Architecture

## Objective

Create a safe commercial billing boundary after Stage 5B without processing real payments yet.

## Implemented

- Replaceable `PaymentProvider` protocol.
- `PlaceholderPaymentProvider` for development and testing.
- Checkout-session persistence.
- Billing-event persistence with unique provider event IDs.
- Idempotent provider-event handling.
- Subscription lifecycle states: active, past_due and cancelled.
- Billing UI showing current plan and checkout architecture status.
- Platform database schema version 4.

## Payment safety

Stage 5C does **not** collect card details, charge customers, store payment credentials, or claim that a payment succeeded. A future provider adapter should receive provider configuration through deployment secrets/environment variables and redirect customers to the provider's hosted checkout.

## Future provider adapters

A provider such as Stripe, Paystack or Flutterwave can implement the `PaymentProvider` boundary. The application subscription service should remain provider-neutral.

A production webhook endpoint must verify the provider's signature before calling `apply_provider_event()`. Webhook events must be idempotent using the provider event ID.

## Recommended next stage

Stage 5D should harden production billing: provider selection, secure configuration, verified webhooks, plan mapping, billing portal/cancellation, and subscription reconciliation. Real charging should only be enabled after those controls are tested.
