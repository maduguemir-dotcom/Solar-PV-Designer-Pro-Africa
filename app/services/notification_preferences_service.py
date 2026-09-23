"""Organization notification preferences and event dispatch helpers."""
from __future__ import annotations
import json
from datetime import datetime, timezone

DEFAULTS = {"proposal_sent": True, "proposal_accepted": True, "proposal_rejected": True, "delivery_failed": True}

class NotificationPreferencesService:
    def __init__(self, database): self.db = database
    def get(self, organization_id):
        with self.db.connect() as c:
            row = c.execute("SELECT preferences_json FROM notification_preferences WHERE organization_id=?", (organization_id,)).fetchone()
        values = dict(DEFAULTS)
        if row:
            values.update(json.loads(row["preferences_json"] or "{}"))
        return values
    def save(self, organization_id, preferences):
        values = dict(DEFAULTS); values.update({k: bool(v) for k,v in preferences.items() if k in DEFAULTS})
        now = datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c:
            c.execute("INSERT INTO notification_preferences (organization_id, preferences_json, updated_at) VALUES (?, ?, ?) ON CONFLICT(organization_id) DO UPDATE SET preferences_json=excluded.preferences_json, updated_at=excluded.updated_at", (organization_id, json.dumps(values, sort_keys=True), now))
        return values
    def enabled(self, organization_id, event_type): return self.get(organization_id).get(event_type, True)
