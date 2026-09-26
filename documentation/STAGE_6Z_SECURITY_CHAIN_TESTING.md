# Stage 6Z — End-to-End Notification Security & Administration Tests

## Purpose

Stage 6Z adds a focused integration test suite for the notification administration
security chain introduced across Stages 6S–6Y. It validates the boundaries between
host-provided identity, role and organization authorization, workspace rendering,
secure recovery operations, durable audit recording, audit history, reliability
summaries, and health snapshots.

## Coverage

- Owner access can reach the workspace and produces an access audit event.
- Staff access is rejected before workspace rendering and is audited as denied.
- Cross-organization workspace access is rejected and records actor/requested
  organization context.
- Secure retry operations require authorization and record successful operations.
- Cross-organization dead-letter recovery is rejected before the queue operation
  is called and records a denied audit event.
- Audit history, reliability summaries, and health snapshots stay scoped to the
  requested organization.
- Audit history rejects a missing organization and an out-of-range limit.

## Run the tests

Run from the repository root after Stages 6S–6Y have been uploaded to the same branch:

```bash
PYTHONPATH=. pytest -q tests/test_stage6z_security_chain.py
```

The test module uses fakes for audit persistence, queue operations, and Streamlit.
It verifies service-level integration contracts but does not replace a deployed
smoke test against the production database, real authentication/session setup,
email provider, or queue worker.

## Deployment checklist

Before production release:

1. Confirm the host application supplies the authenticated user ID, role, and
   organization from trusted server-side session state—not from editable widgets.
2. Confirm the admin navigation calls `NotificationAdminIntegration.render()`.
3. Supply the same durable audit service to access auditing and secure recovery.
4. Confirm the recovery UI receives `SecureNotificationOperations`, never the raw
   queue operations service.
5. Run the full repository test suite and a staging smoke test with two separate
   organizations and owner/admin/engineer/staff accounts.
6. Review audit retention, access to audit records, and backup/restore procedures.

## Scope note

This stage adds tests and integration guidance only. It does not claim that the
production application has been deployed or that its main navigation is wired
unless that integration is completed in the host repository.
