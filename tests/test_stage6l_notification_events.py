from app.services.notification_event_service import NotificationEventService

class C:
    def __init__(self): self.rows = {}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def execute(self, sql, params=()):
        class R:
            def __init__(self, row=None): self.row=row
            def fetchone(self): return self.row
        if sql.startswith("SELECT preferences_json"):
            return R(None)
        return R(None)
class DB:
    def connect(self): return C()
class N:
    def queue_notification(self, **kwargs): return "n-1"

def test_disabled_preference_skips_queue():
    svc = NotificationEventService(DB(), N())
    svc.preferences.enabled = lambda org, event: False
    result = svc.dispatch("org", "proposal_sent", "a@b.com", "Subject", "Body")
    assert result["status"] == "skipped"

def test_enabled_preference_queues():
    svc = NotificationEventService(DB(), N())
    svc.preferences.enabled = lambda org, event: True
    result = svc.dispatch("org", "proposal_sent", "a@b.com", "Subject", "Body")
    assert result["status"] == "queued"
    assert result["notification_id"] == "n-1"
