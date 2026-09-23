# Stage 6N — Notification Reliability & Background Processing

Adds retry/recovery service for queued notifications, including due-item claiming, retry scheduling, and terminal `dead_letter` status after the configured maximum attempts.

## GitHub upload
- `app/services/notification_reliability_service.py`
- `app/platform/schema.py`
- `tests/test_stage6n_reliability.py`
- this documentation file

Commit: `Stage 6N - Add notification reliability and retry controls`
Remain on `development-v3.0`; do not merge into `main`.
