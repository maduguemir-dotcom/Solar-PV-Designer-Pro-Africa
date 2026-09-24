# Stage 6W — Notification Administration Workspace Integration

## Purpose

Stage 6W provides a clean integration boundary for bringing the Stage 6V
notification health dashboard into the application's existing administrator
workspace.

## What is included

- `NotificationAdminIntegration`: dependency-injection/composition boundary.
- `render_notification_admin_workspace`: Streamlit administration workspace.
- Four administrator sections: Health, Audit History, Reliability, Recovery.
- Organization ID validation before rendering.
- Tests for dependency routing and invalid configuration.

## Host application integration

The existing application's admin/navigation module should instantiate
`NotificationAdminIntegration` with the existing Stage 6V health service and
Stage 6S/6T/6U renderers, then call `integration.render(current_organization_id)`
from the appropriate administrator-only route.

This Stage-Only package intentionally does **not** overwrite the application's
unknown main navigation file. That preserves the existing project structure and
avoids replacing unrelated application code. The host application's current
admin entry point should therefore be wired to this integration boundary.

## Security boundary

This workspace does not implement an alternative authorization mechanism.
Recovery actions must continue to use the Stage 6S secure operations layer.
All data displayed by the workspace must be scoped to the authenticated
organization.

## Validation

Run:

```text
PYTHONPATH=. pytest -q tests/test_stage6w_admin_integration.py
python -m py_compile app/services/notification_admin_integration.py app/ui/notification_admin_workspace.py tests/test_stage6w_admin_integration.py
```

## GitHub

Upload the Stage 6W files to `development-v3.0`.

Commit message:

`Stage 6W - Integrate notification operations into admin workspace`

Do not merge into `main` yet.
