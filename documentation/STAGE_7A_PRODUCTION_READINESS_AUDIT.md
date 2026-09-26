# Stage 7A — Production Readiness & Full-Application Integration Audit

**Project:** Solar PV Designer Pro Africa™  
**Branch target:** `development-v3.0`  
**Audit scope:** Reconstructed cumulative source available from Stage 6M plus Stage 6N–6Z stage archives.  
**Stage type:** Audit and remediation planning only; no application source files are changed by this package.

## Executive summary

The notification administration work has useful service-level components and focused tests, but the cumulative application is **not ready to be treated as production-integrated**. The audit found an implementation collision between queue reliability and audit-derived reliability, stale tests after an interface change, an administration workspace that is not wired into `app/main.py`, and an audit-schema edge case for unauthenticated access attempts.

Do not merge the notification administration work into `main` until the P1 findings below are fixed and the full suite passes in the intended deployment environment.

## Findings

### P1 — Stage 6U overwrites the Stage 6N/6O queue reliability service

**Evidence:** Stage 6O defines `NotificationReliabilityService(database, max_attempts=..., retry_delay_minutes=...)` with queue methods such as `claim_due`, `record_success`, `record_failure`, `recoverable`, and queue `metrics`. Stage 6U uses the same module path, `app/services/notification_reliability_service.py`, and the same class name for audit-derived metrics with constructor `NotificationReliabilityService(audit_service)` and methods `summarize` and `daily_trend`.

**Observed consequence:** When Stage 6U is applied after Stage 6O as instructed, the Stage 6O test fails at construction: `TypeError: NotificationReliabilityService.__init__() got an unexpected keyword argument 'max_attempts'`. This is a real cumulative integration regression, not merely a missing dependency.

**Required fix:** Keep the responsibilities separate, e.g. rename the queue component to `NotificationQueueReliabilityService` in `notification_queue_reliability_service.py`, and keep audit-derived analytics as `NotificationReliabilityService` or rename it to `NotificationAuditAnalyticsService`. Update imports and tests together.

### P1 — Notification administration is not connected to the main application entry point

**Evidence:** `app/main.py` imports and renders notification preferences, but does not import or invoke `NotificationAdminIntegration` or `render_notification_admin_workspace`. The Stage 6W–6Y modules therefore remain integration components rather than an accessible administrator workflow in the main app.

**Required fix:** Add a navigation entry visible only to authorized users. Build the actor context from the existing authenticated session, derive the organization from trusted session/database context, and invoke the Stage 6Y audited authorization boundary before rendering any administration component. Do not accept actor role or organization IDs from editable form fields.

### P1 — Missing actor IDs cannot be written to the durable audit table

**Evidence:** `notification_audit_events.actor_user_id` is declared `TEXT NOT NULL`, while the administration access boundary is designed to audit denied requests including a missing authenticated actor. The durable audit insert therefore cannot persist a denial when `actor_user_id` is absent.

**Required fix:** Decide and document a safe representation for unauthenticated attempts. Options include allowing a nullable actor ID and recording an explicit unauthenticated principal, or using a fixed system sentinel while retaining the denial reason. Add a real-database test for this path. Never silently discard the denial event.

### P1 — Cumulative tests contain stale interface expectations

**Evidence:** The Stage 6W test calls `NotificationAdminIntegration.render("")`, but Stage 6X changed `render` to require keyword-only authenticated actor and organization context. Running the Stage 6V–6Z tests together fails with `TypeError: NotificationAdminIntegration.render() takes 1 positional argument but 2 were given`.

**Required fix:** Update Stage 6W tests to use the current secure API and assert authorization/audit behavior. Preserve regression coverage rather than skipping the old test.

### P1 — Test import conventions are inconsistent

**Evidence:** Some tests import modules as `app.services...`, while older tests import `services...`. The repository `pytest.ini` sets `pythonpath = .`, which supports the former but not consistently the latter. Adding `app` to `PYTHONPATH` can make `app/platform` shadow Python's standard-library `platform` module in plugin startup.

**Required fix:** Standardize test imports and application package boundaries. Avoid adding the `app` directory globally to `PYTHONPATH` as a workaround. Run the suite using the documented project-root command after cleanup.

### P2 — Full suite has not been validated in a fully provisioned environment

**Evidence:** Collection of the broad test suite in this audit environment stopped because `streamlit` was not installed. `requirements.txt` does list Streamlit, so this may be an environment setup issue rather than an application defect.

**Required fix:** Install the declared dependencies in a clean environment and run the complete test suite. Record the Python version and test results in CI or release documentation.

## Validation performed

- Python compilation of the reconstructed `app` and `tests` trees completed successfully.
- Focused Stage 6P–6T tests passed before the run reached the Stage 6U reliability test.
- Stage 6O queue-monitoring regression test failed after Stage 6U's same-path service replacement.
- Stage 6V–6Z test run passed the Stage 6V tests, then failed on the stale Stage 6W test interface.
- Stage 6X–6Z tests passed independently: 15 passed.
- The broad suite could not be collected because `streamlit` was absent from the audit environment.

These results are from the available Stage 6M cumulative archive with Stage 6N–6Z archives overlaid in stage order; they are not a live test of the user's GitHub checkout or deployed application.

## Release gate

Before merging into `main`:

1. Resolve all P1 findings.
2. Add integration tests for the durable audit service against the actual database adapter, including unauthenticated denial.
3. Confirm the main app's navigation invokes the secure administration integration using trusted session identity.
4. Install declared requirements in a clean environment.
5. Run all tests, then perform a staging smoke test for login, organization switching, admin workspace access, audit history, reliability metrics, and recovery controls.
6. Review payment/webhook, email, document access, and tenant isolation separately before public SaaS launch.
