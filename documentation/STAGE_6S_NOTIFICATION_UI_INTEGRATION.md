# Stage 6S — Notification Operations UI Integration & End-to-End Security Testing

## Purpose

Stage 6S connects the notification operations UI recovery buttons to the Stage 6R secure operations boundary. Recovery actions must use authenticated actor context rather than trusting values entered in the UI.

## Integration

Update the existing dashboard call from:

```python
render_notification_operations(service, organization_id)
```

to:

```python
render_notification_operations(
    service,
    organization_id,
    actor={
        "role": current_user.role,
        "user_id": current_user.id,
        "organization_id": current_user.organization_id,
    },
    secure_service=secure_notification_operations,
)
```

Use the application's actual authenticated-user object/field names. Do not expose role or organization scope as editable Streamlit controls.

## Security behavior

- Only `owner` and `admin` roles are accepted by the existing security policy.
- The actor organization must equal the target organization.
- Retry and dead-letter recovery are executed only through `SecureNotificationOperations`.
- Allowed and denied recovery attempts receive durable audit records.
- The UI disables recovery controls when secure operations or authenticated actor context are unavailable.

## Upload

This Stage-Only ZIP is intended to be applied after Stage 6R. It contains only modified/new files for Stage 6S.
