import pytest
from app.services.notification_audit_history_service import NotificationAuditHistoryService


class FakeAudit:
    def list_events(self, organization_id, limit=100):
        return [
            {"organization_id": organization_id, "outcome": "allowed", "action": "retry_failed", "actor_user_id": "u1"},
            {"organization_id": organization_id, "outcome": "denied", "action": "retry_failed", "actor_user_id": "u2"},
            {"organization_id": organization_id, "outcome": "allowed", "action": "requeue_dead_letter", "actor_user_id": "u1"},
        ][:limit]


def test_history_is_organization_scoped_and_filterable():
    svc = NotificationAuditHistoryService(FakeAudit())
    rows = svc.list_history("org-1", outcome="denied")
    assert len(rows) == 1
    assert rows[0]["organization_id"] == "org-1"
    assert rows[0]["actor_user_id"] == "u2"


def test_history_action_filter():
    svc = NotificationAuditHistoryService(FakeAudit())
    rows = svc.list_history("org-1", action="requeue_dead_letter")
    assert len(rows) == 1
    assert rows[0]["action"] == "requeue_dead_letter"


def test_history_validates_inputs():
    svc = NotificationAuditHistoryService(FakeAudit())
    with pytest.raises(ValueError):
        svc.list_history("")
    with pytest.raises(ValueError):
        svc.list_history("org-1", limit=501)
