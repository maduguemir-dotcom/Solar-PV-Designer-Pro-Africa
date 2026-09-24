# Stage 6U — Notification Operations Analytics & Reliability Metrics

Stage 6U adds an organization-scoped analytics layer over the durable notification audit trail introduced in Stage 6R and surfaced in Stage 6T.

## Metrics

- Total audit events analyzed
- Allowed and denied administrative operations
- Authorization success rate
- Denial rate
- Retry-failed operation count
- Dead-letter requeue operation count
- Daily audit activity trend

## Important scope

These are **audit-derived reliability indicators**. They do not claim to replace direct queue telemetry, delivery-provider metrics, latency measurements, or message-level success/failure data. Those can be integrated later when the production queue/provider exposes them.

## Integration

Instantiate `NotificationReliabilityService` with the existing durable audit service and render it through `render_notification_reliability(...)` in an organization-scoped administration dashboard.
