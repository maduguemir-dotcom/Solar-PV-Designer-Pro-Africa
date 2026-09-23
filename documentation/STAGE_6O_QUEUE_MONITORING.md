# Stage 6O — Notification Reliability Integration & Queue Monitoring

Adds attempt counting during claims, success recording, queue metrics, failure-rate calculation, and attention-required monitoring.

## Validation

Run from repository root:

```bash
python -m pytest tests/test_stage6o_queue_monitoring.py -q
```

The service expects the existing `notification_queue` table from Stage 6N.
