# Stage 6Y — Administration Security Audit Integration

## Purpose

Stage 6Y connects the notification administration access boundary to the existing durable audit architecture without taking ownership of the application's database or authentication system.

## Audit events

Each administration workspace access decision produces an audit event with:

- organization ID
- actor user ID
- action: `notification_admin_access`
- target: `notification_operations_workspace`
- outcome: `allowed` or `denied`
- actor role and organization
- requested organization
- denial reason when applicable

## Integration

Inject the existing durable audit service (for example, the project's Stage 6R `DurableAuditService`) through `NotificationAdminSecurityAudit`.

The access boundary records the event before returning an authorization result or raising `PermissionError`.

## Security properties

- Authentication remains owned by the host application.
- Only `owner` and `admin` roles are accepted.
- Cross-organization access is denied and audited.
- Unauthorized users cannot reach the administration workspace renderer.
- No direct database dependency is introduced into the access adapter.

## Production wiring

Construct:

```python
security_audit = NotificationAdminSecurityAudit(durable_audit_service)
```

and pass it to `NotificationAdminIntegration(..., security_audit=security_audit)`.

The durable audit service must be the application's existing organization-aware implementation. Do not create a second audit database.
