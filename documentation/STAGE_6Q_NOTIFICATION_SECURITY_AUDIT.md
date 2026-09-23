# Stage 6Q — Notification Security, Role Authorization & Audit Controls

This stage adds reusable security helpers for notification administration.

## Controls
- Only `owner` and `admin` roles are authorized by default.
- Actor organization must match the target organization.
- Allowed and denied actions can be sent to an audit sink.
- No credentials or secrets are stored.

## Integration requirement
Wrap the Stage 6P retry/requeue UI and service calls with `authorize_and_record(...)`.
Persist `AuditEvent` records in the platform database using a dedicated organization-scoped
 audit table before production deployment. Do not rely only on in-memory callbacks.
