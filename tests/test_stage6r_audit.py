import sqlite3
from types import SimpleNamespace
from app.services.durable_audit_service import DurableAuditService

class DB:
    def __init__(self): self.conn = sqlite3.connect(":memory:")
    def connect(self):
        self.conn.row_factory = sqlite3.Row
        return self.conn

def test_durable_audit_round_trip():
    db = DB(); service = DurableAuditService(db)
    event_id = service.record(organization_id="org1", actor_user_id="u1", action="retry_failed", target="queue", outcome="allowed", details={"count": 2})
    rows = service.list_events("org1")
    assert event_id == 1
    assert len(rows) == 1
    assert rows[0]["action"] == "retry_failed"
