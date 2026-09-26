# Stage 7B — Reliability Service Separation & Regression Repair

## Purpose

Stage 6O's queue telemetry service and Stage 6U's audit-derived analytics service previously used the same module path. The later implementation replaced the earlier queue service, breaking the `NotificationReliabilityService(database, ...)` constructor expected by queue monitoring and queue tests.

## Changes

- Restores `app/services/notification_reliability_service.py` as the queue-backed service from Stage 6O. It supports claiming due notifications, recording success/failure, listing recoverable items, and queue status metrics.
- Moves Stage 6U audit-derived metrics into `app/services/notification_audit_analytics_service.py` without changing its public analytics methods (`summarize`, `daily_trend`).
- Updates the Stage 6U tests to import the explicitly named audit analytics service.
- Updates the Stage 6W integration tests to call the Stage 6X+ authorization-aware `render(...)` interface using authenticated actor context.
- Adds regression tests proving the two services can coexist and organization-scoped analytics still work.

## Integration notes

The Stage 6U reliability UI takes its service as an injected dependency, so the host app should inject `NotificationReliabilityService` from `notification_audit_analytics_service.py` into that UI. Queue workers and `NotificationQueueMonitor` should use `NotificationReliabilityService` from `notification_reliability_service.py`.

Suggested explicit aliases:

```python
from app.services.notification_reliability_service import (
    NotificationReliabilityService as NotificationQueueReliabilityService,
)
from app.services.notification_audit_analytics_service import (
    NotificationReliabilityService as NotificationAuditAnalyticsService,
)
```

## Validation

Run from the repository root:

```bash
PYTHONPATH=. pytest -q tests/test_stage6o_queue_monitoring.py tests/test_stage6u_reliability.py tests/test_stage6w_admin_integration.py tests/test_stage7b_regression_repair.py
```

The package does not change the main navigation or claim that the full production application is integrated. Validate the host app and full test suite after uploading these files.
