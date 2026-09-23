"""Retry and recovery controls for queued notifications."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone

class NotificationReliabilityService:
    def __init__(self, database, max_attempts=3, retry_delay_minutes=5):
        self.db = database
        self.max_attempts = max_attempts
        self.retry_delay_minutes = retry_delay_minutes

    def claim_due(self, limit=20):
        now = datetime.now(timezone.utc).isoformat()
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM notification_queue WHERE status IN ('queued','failed') AND attempts < ? AND (next_attempt_at IS NULL OR next_attempt_at <= ?) ORDER BY created_at LIMIT ?", (self.max_attempts, now, limit)).fetchall()
            ids = [r['id'] for r in rows]
            for item_id in ids:
                conn.execute("UPDATE notification_queue SET status='processing' WHERE id=?", (item_id,))
        return rows

    def record_failure(self, notification_id, error):
        now = datetime.now(timezone.utc)
        with self.db.connect() as conn:
            row = conn.execute("SELECT attempts FROM notification_queue WHERE id=?", (notification_id,)).fetchone()
            if not row:
                raise ValueError('Notification not found')
            attempts = int(row['attempts'])
            terminal = attempts >= self.max_attempts
            next_at = None if terminal else (now + timedelta(minutes=self.retry_delay_minutes)).isoformat()
            status = 'dead_letter' if terminal else 'failed'
            conn.execute("UPDATE notification_queue SET status=?, last_error=?, next_attempt_at=? WHERE id=?", (status, str(error), next_at, notification_id))
            return {'id': notification_id, 'status': status, 'attempts': attempts, 'next_attempt_at': next_at}

    def recoverable(self, limit=100):
        with self.db.connect() as conn:
            return conn.execute("SELECT * FROM notification_queue WHERE status='failed' AND attempts < ? ORDER BY created_at LIMIT ?", (self.max_attempts, limit)).fetchall()
