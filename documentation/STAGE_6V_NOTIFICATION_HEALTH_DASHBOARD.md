# Stage 6V — Notification Operations Health Dashboard

Stage 6V adds a composed administrator-facing notification operations health view.

## Scope

- Combines Stage 6U reliability metrics with durable audit history.
- Shows organization-scoped authorization/recovery activity.
- Shows the latest audit event without executing any operation.
- Provides integration points for the existing audit-history and secure-recovery UI.
- Recovery actions remain behind the Stage 6S secure operations boundary.

## Integration

Import `render_notification_health_dashboard` from
`app.ui.notification_health_dashboard` and inject the existing Stage 6U
reliability renderer, Stage 6T audit-history renderer, and Stage 6S recovery
renderer where those components are available.

The health service is read-only. It must not be used as a bypass around
`SecureNotificationOperations`.
