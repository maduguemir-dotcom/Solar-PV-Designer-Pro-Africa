# Stage 7A — Prioritized Remediation Backlog

| Priority | Work item | Acceptance criteria |
|---|---|---|
| P1 | Separate queue reliability from audit analytics | Stage 6O queue methods and Stage 6U analytics coexist under distinct service modules; both test groups pass. |
| P1 | Wire notification admin into `app/main.py` | Authorized owner/admin can reach it through navigation; staff/engineer and cross-organization attempts are rejected before rendering. |
| P1 | Make denied unauthenticated access auditable | Durable audit record persists when no user ID is available; real database test covers it. |
| P1 | Update stale Stage 6W tests | Tests use the Stage 6X keyword-only secure API and assert denial/audit outcomes. |
| P1 | Standardize imports and test invocation | Test suite runs from repository root without adding `app` to `PYTHONPATH`; no stdlib module shadowing. |
| P2 | Provision reproducible CI/test environment | Clean install from `requirements.txt`; full suite results are captured. |
| P2 | Run production staging checks | Login, tenant isolation, admin access, notification history, metrics, retry/requeue, and audit trail are exercised end-to-end. |

## Recommended next implementation stage

**Stage 7B — Reliability Service Separation & Regression Repair.** Fix the service-name collision and stale Stage 6W tests first. Do not begin new notification features until those regressions are resolved.
