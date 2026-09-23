from datetime import datetime, timezone

class NotificationOperationsService:
    """Organization-scoped operational controls for the notification queue."""
    def __init__(self, db):
        self.db = db

    def _conn(self):
        return self.db.connect()

    def metrics(self, organization_id):
        conn = self._conn()
        rows = conn.execute("""SELECT status, COUNT(*) AS count FROM notification_queue
                              WHERE organization_id=? GROUP BY status""", (organization_id,)).fetchall()
        result = {"queued": 0, "processing": 0, "sent": 0, "failed": 0, "dead_letter": 0}
        for row in rows:
            result[row["status"]] = row["count"]
        result["total"] = sum(result.values())
        result["attention_required"] = result["failed"] + result["dead_letter"]
        return result

    def retry_failed(self, organization_id, limit=25):
        now = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        cur = conn.execute("""UPDATE notification_queue SET status='queued', next_attempt_at=?, last_error=NULL
                             WHERE organization_id=? AND status='failed' AND attempts < 3
                             AND id IN (SELECT id FROM notification_queue WHERE organization_id=? AND status='failed' LIMIT ?)""",
                          (now, organization_id, organization_id, int(limit)))
        conn.commit()
        return cur.rowcount

    def requeue_dead_letter(self, organization_id, limit=25):
        now = datetime.now(timezone.utc).isoformat()
        conn = self._conn()
        cur = conn.execute("""UPDATE notification_queue SET status='queued', next_attempt_at=?, last_error=NULL, attempts=0
                             WHERE organization_id=? AND status='dead_letter'
                             AND id IN (SELECT id FROM notification_queue WHERE organization_id=? AND status='dead_letter' LIMIT ?)""",
                          (now, organization_id, organization_id, int(limit)))
        conn.commit()
        return cur.rowcount
