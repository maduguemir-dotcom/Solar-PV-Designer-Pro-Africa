import sqlite3
from app.services.notification_reliability_service import NotificationReliabilityService as QueueReliabilityService
from app.services.notification_audit_analytics_service import NotificationReliabilityService as AuditAnalyticsService
from app.services.notification_queue_monitor import NotificationQueueMonitor


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE notification_queue (id TEXT PRIMARY KEY, organization_id TEXT, status TEXT, attempts INTEGER, next_attempt_at TEXT, last_error TEXT, created_at TEXT)"
        )

    def connect(self):
        return self.conn


def test_queue_reliability_constructor_and_metrics_are_restored():
    db = DB()
    db.conn.execute("INSERT INTO notification_queue VALUES ('n1','org1','queued',0,NULL,NULL,'2026-01-01')")
    db.conn.commit()
    service = QueueReliabilityService(db, max_attempts=3, retry_delay_minutes=0)
    rows = service.claim_due()
    assert len(rows) == 1
    assert service.metrics("org1")["processing"] == 1
    assert NotificationQueueMonitor(service).summary("org1")["attention_required"] is False


def test_audit_analytics_uses_separate_service_and_preserves_rates():
    class Audit:
        def list_events(self, organization_id, limit=500):
            assert organization_id == "org1"
            return [
                {"organization_id": "org1", "outcome": "allowed", "action": "retry_failed", "created_at": "2026-09-25T08:00:00"},
                {"organization_id": "org1", "outcome": "denied", "action": "requeue_dead_letter", "created_at": "2026-09-25T09:00:00"},
            ][:limit]

    analytics = AuditAnalyticsService(Audit())
    summary = analytics.summarize("org1")
    assert summary["total_events"] == 2
    assert summary["denial_rate"] == 50.0
    assert summary["retry_failed_events"] == 1
    assert analytics.daily_trend("org1")[0]["total"] == 2


def test_missing_organization_is_rejected_by_analytics():
    analytics = AuditAnalyticsService(object())
    try:
        analytics.summarize("")
    except ValueError as exc:
        assert "organization_id" in str(exc)
    else:
        raise AssertionError("missing organization must be rejected")
