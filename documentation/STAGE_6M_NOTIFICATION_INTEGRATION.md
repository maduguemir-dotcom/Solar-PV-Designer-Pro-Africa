# Stage 6M — Proposal Status Notification Integration

This stage connects proposal status transitions to the preference-aware notification dispatcher.

- `sent`, `accepted`, and `rejected` transitions can dispatch notification events.
- Dispatch is optional and injected, preserving separation of concerns.
- Notifications are only attempted after a valid organization-scoped update.
- `pytest.ini` establishes the repository root as the test import path and avoids using `app` as the top-level path, reducing the `platform` namespace collision.

Production email delivery remains controlled by the existing provider configuration and queue.
