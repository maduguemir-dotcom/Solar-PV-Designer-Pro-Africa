from app.services.notification_health_service import NotificationHealthService


class FakeReliability:
    def summarize(self, organization_id, limit=500):
        return {
            "total_events": 2,
            "allowed_events": 1,
            "denied_events": 1,
            "authorization_success_rate": 50.0,
            "denial_rate": 50.0,
            "retry_failed_events": 1,
            "requeue_dead_letter_events": 0,
        }


class FakeAudit:
    def list_events(self, organization_id, limit=500):
        return [{"created_at": "2026-09-24T09:00:00", "action": "retry_failed", "outcome": "allowed"}]


def test_snapshot_is_organization_scoped_and_composed():
    result = NotificationHealthService(FakeReliability(), FakeAudit()).snapshot("org-1")
    assert result["organization_id"] == "org-1"
    assert result["summary"]["total_events"] == 2
    assert result["audit_events_available"] == 1
    assert result["latest_event"]["action"] == "retry_failed"


def test_snapshot_requires_organization_id():
    try:
        NotificationHealthService(FakeReliability(), FakeAudit()).snapshot("")
        assert False
    except ValueError as exc:
        assert "organization_id" in str(exc)


def test_empty_audit_has_no_latest_event():
    class EmptyAudit:
        def list_events(self, organization_id, limit=500):
            return []

    result = NotificationHealthService(FakeReliability(), EmptyAudit()).snapshot("org-1")
    assert result["latest_event"] is None
    assert result["audit_events_available"] == 0
