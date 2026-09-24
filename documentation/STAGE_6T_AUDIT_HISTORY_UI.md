# Stage 6T — Notification Audit & Operations History UI

Stage 6T adds a read-only, organization-scoped view of durable notification recovery audit events.

## Files

- `app/services/notification_audit_history_service.py` — filter/query boundary over the durable audit service.
- `app/ui/notification_audit_history.py` — Streamlit audit history table and filters.
- `app/ui/notification_operations.py` — exposes a helper for placing the audit section below operations controls.
- `tests/test_stage6t_audit_history.py` — service filtering and validation tests.

## Integration

The authenticated application should construct `NotificationAuditHistoryService` with the existing Stage 6R `DurableAuditService`, then call:

```python
render_notification_audit_section(history_service, organization_id)
```

Use the authenticated organization ID only. The history service is read-only and does not provide a recovery or mutation path.

## Security notes

- Organization ID is mandatory.
- Filtering happens after retrieval from the organization-scoped durable audit service.
- No role or organization can be supplied from a Streamlit widget.
- Recovery actions remain behind `SecureNotificationOperations` from Stage 6S.
- This stage does not expose raw database connections to the UI.
