from app.services.notification_reliability_service import NotificationReliabilityService


class FakeAudit:
    def list_events(self, organization_id, limit=500):
        return [
            {"organization_id": organization_id, "outcome": "allowed", "action": "retry_failed", "created_at": "2026-09-24T08:00:00"},
            {"organization_id": organization_id, "outcome": "denied", "action": "retry_failed", "created_at": "2026-09-24T09:00:00"},
            {"organization_id": organization_id, "outcome": "allowed", "action": "requeue_dead_letter", "created_at": "2026-09-24T09:30:00"},
        ][:limit]


def test_summary_counts_and_rates():
    svc = NotificationReliabilityService(FakeAudit())
    result = svc.summarize("org-1")
    assert result["total_events"] == 3
    assert result["allowed_events"] == 2
    assert result["denied_events"] == 1
    assert round(result["authorization_success_rate"], 2) == 66.67
    assert result["retry_failed_events"] == 2
    assert result["requeue_dead_letter_events"] == 1


def test_daily_trend_groups_events_by_date():
    svc = NotificationReliabilityService(FakeAudit())
    result = svc.daily_trend("org-1")
    assert len(result) == 1
    assert result[0]["date"] == "2026-09-24"
    assert result[0]["total"] == 3
    assert result[0]["allowed"] == 2
    assert result[0]["denied"] == 1


def test_empty_data_has_zero_rates():
    class EmptyAudit:
        def list_events(self, organization_id, limit=500):
            return []

    result = NotificationReliabilityService(EmptyAudit()).summarize("org-1")
    assert result["total_events"] == 0
    assert result["denial_rate"] == 0.0
