import sqlite3
from app.services.notification_reliability_service import NotificationReliabilityService
from app.services.notification_queue_monitor import NotificationQueueMonitor

class DB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE notification_queue (id TEXT PRIMARY KEY, organization_id TEXT, status TEXT, attempts INTEGER, next_attempt_at TEXT, last_error TEXT, created_at TEXT)")
    def connect(self):
        return self.conn

def test_claim_increments_attempts_and_metrics():
    db = DB()
    db.conn.execute("INSERT INTO notification_queue VALUES ('n1','o1','queued',0,NULL,NULL,'2026-01-01')")
    db.conn.commit()
    service = NotificationReliabilityService(db, max_attempts=3)
    rows = service.claim_due()
    assert len(rows) == 1
    row = db.conn.execute("SELECT attempts,status FROM notification_queue WHERE id='n1'").fetchone()
    assert (row['attempts'], row['status']) == (1, 'processing')
    service.record_success('n1')
    assert NotificationQueueMonitor(service).summary('o1')['sent'] == 1
