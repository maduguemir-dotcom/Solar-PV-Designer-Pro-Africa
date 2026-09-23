"""Durable, organization-scoped audit logging for administrative actions (Stage 6R)."""
import json
from datetime import datetime, timezone

class DurableAuditService:
    def __init__(self, db):
        self.db = db
        self.ensure_table()

    def _conn(self):
        return self.db.connect()

    def ensure_table(self):
        conn = self._conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS notification_audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id TEXT NOT NULL,
            actor_user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            outcome TEXT NOT NULL,
            details_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notification_audit_org ON notification_audit_events(organization_id, created_at)")
        conn.commit()

    def record(self, *, organization_id, actor_user_id, action, target, outcome, details=None):
        created_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(details or {}, sort_keys=True, default=str)
        conn = self._conn()
        cur = conn.execute("""INSERT INTO notification_audit_events
            (organization_id, actor_user_id, action, target, outcome, details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (organization_id, actor_user_id, action, target, outcome, payload, created_at))
        conn.commit()
        return cur.lastrowid

    def list_events(self, organization_id, limit=100):
        conn = self._conn()
        return conn.execute("""SELECT * FROM notification_audit_events
            WHERE organization_id=? ORDER BY id DESC LIMIT ?""", (organization_id, int(limit))).fetchall()
