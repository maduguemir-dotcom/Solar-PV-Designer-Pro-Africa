import sqlite3
from app.services.notification_operations_service import NotificationOperationsService

class DB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE notification_queue (id TEXT PRIMARY KEY, organization_id TEXT, status TEXT, attempts INTEGER, next_attempt_at TEXT, last_error TEXT, created_at TEXT)")
    def connect(self): return self.conn

def test_metrics_and_recovery_are_organization_scoped():
    db = DB()
    db.conn.executemany("INSERT INTO notification_queue VALUES (?,?,?,?,?,?,?)", [
        ("a","o1","failed",1,None,"x","2026-01-01"),
        ("b","o1","dead_letter",3,None,"x","2026-01-01"),
        ("c","o2","failed",1,None,"x","2026-01-01"),
    ])
    db.conn.commit()
    svc = NotificationOperationsService(db)
    assert svc.metrics("o1")["attention_required"] == 2
    assert svc.retry_failed("o1") == 1
    assert svc.requeue_dead_letter("o1") == 1
    assert db.conn.execute("SELECT status FROM notification_queue WHERE id='c'").fetchone()[0] == "failed"
