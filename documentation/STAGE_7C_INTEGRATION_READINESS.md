# Stage 7C — Full-Application Integration Readiness Gate

## Purpose

Stage 7C adds a read-only pre-deployment checker for the notification administration workflow. It checks that expected Stage 6R–6Y service/UI modules exist and that a recognized application entry point contains an explicit notification administration integration marker.

## Important limitation

This stage does **not** edit or wire the host application's `app/main.py`. The current cumulative development checkout was not provided in this stage's working source, so changing its entry point without seeing its current navigation and authentication flow would be unsafe. The checker deliberately reports a missing entry-point hook rather than claiming integration is complete.

## Run

From the repository root:

```bash
PYTHONPATH=. pytest -q tests/test_stage7c_readiness.py
```

Programmatic use:

```python
from app.services.notification_integration_readiness import NotificationIntegrationReadiness

report = NotificationIntegrationReadiness(".").run()
print(report)
if not report["ready"]:
    raise SystemExit("Notification integration readiness checks failed")
```

The default check expects the audit, secure operations, reliability, analytics, history, health, access, security-audit, integration and UI modules created in earlier stages. If your current branch has intentionally renamed a module, update `REQUIRED_FILES` only after verifying the replacement and its callers.

## Release gate

A passing static readiness report is necessary but not sufficient. Before release:

1. Run the full test suite with all project dependencies installed.
2. Verify the actual entry-point call uses the authenticated session user and organization from the host app, not user-supplied form fields.
3. Run staging tests for owner/admin access, engineer/staff denial, cross-organization denial, durable audit writes, and recovery operations.
4. Confirm the live database schema and migration sequence are current.
5. Verify Streamlit startup and the complete admin workflow manually in a staging deployment.

Do not merge into `main` solely because this readiness checker passes.
