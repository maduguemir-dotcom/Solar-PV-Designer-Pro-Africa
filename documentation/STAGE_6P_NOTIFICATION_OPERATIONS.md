# Stage 6P — Notification Operations Dashboard & Administrative Controls

Adds organization-scoped queue metrics and controlled recovery actions for failed and dead-letter notifications.

## Integration

Add the operations page to the authenticated navigation and instantiate `NotificationOperationsService` with the existing platform database. Keep all actions organization-scoped and restrict them to authorized administrative roles.

## Validation

```bash
python -m pytest tests/test_stage6p_operations.py -q
```
