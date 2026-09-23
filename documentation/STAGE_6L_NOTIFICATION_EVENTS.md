# Stage 6L — Preference-Aware Notification Events

## Scope

Adds a small event-dispatch layer between business events and the durable notification queue.

## Behavior

- Checks organization notification preferences before queueing.
- Returns `skipped` when an event is disabled.
- Queues supported events through the existing NotificationService.
- Keeps email delivery provider-independent.

## Integration guidance

Use `NotificationEventService.dispatch(...)` from proposal status transitions. Do not send email directly from UI code. Production workers should deliver queued notifications separately.
