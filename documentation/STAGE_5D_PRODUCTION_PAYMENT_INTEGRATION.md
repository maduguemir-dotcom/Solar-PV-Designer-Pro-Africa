# Stage 5D — Production Payment Integration & Subscription Reconciliation

Stage 5D hardens the Stage 5C billing boundary for eventual production payment providers.

## Implemented
- HMAC-SHA256 signed webhook verification.
- Reject-before-process behavior for invalid signatures.
- Idempotent provider event processing using the existing unique provider event ID.
- Provider subscription ID persistence.
- Sandbox provider for safe end-to-end billing tests; it never charges real money.
- Checkout session status updates when a provider event is received.
- Subscription lifecycle handling for activation/update, payment failure and cancellation.
- Provider-independent billing orchestration.

## Production safety
Real provider secrets must be supplied through deployment secrets/environment variables.
Do not commit API keys, webhook secrets, customer payment data, or provider credentials.
The sandbox adapter intentionally uses a non-routable checkout URL and cannot charge money.

## Future provider adapters
A production adapter can implement the existing `PaymentProvider` contract and translate
provider-specific events into the normalized events consumed by `BillingService`.
Suitable candidates include Stripe, Paystack, or Flutterwave depending on the target market,
merchant account availability, currency support and regulatory requirements.

## Recommended production event flow
1. Customer selects a paid plan.
2. Application creates a provider checkout session.
3. Customer completes payment at the provider.
4. Provider sends a signed webhook.
5. Application verifies the signature before parsing/trusting the event.
6. Application rejects duplicate provider event IDs.
7. Subscription is activated/updated only after the verified event.
8. Entitlements are read from the subscription service.
9. Renewal/failure/cancellation events keep the subscription state synchronized.
10. A scheduled reconciliation job can later compare local state with provider state.

Live charging is **not enabled by Stage 5D**.
