"""Audit-derived notification reliability metrics (Stage 6U)."""
from collections import Counter, defaultdict
from datetime import datetime


class NotificationReliabilityService:
    """Build organization-scoped reliability metrics from durable audit events.

    These are audit-derived operational indicators, not direct queue telemetry.
    """

    def __init__(self, audit_service):
        self.audit_service = audit_service

    def _events(self, organization_id, limit=500):
        if not organization_id:
            raise ValueError("organization_id is required")
        if limit < 1 or limit > 5000:
            raise ValueError("limit must be between 1 and 5000")
        return self.audit_service.list_events(organization_id, limit=limit)

    def summarize(self, organization_id, *, limit=500):
        events = self._events(organization_id, limit)
        outcomes = Counter(e.get("outcome", "unknown") for e in events)
        actions = Counter(e.get("action", "unknown") for e in events)
        total = len(events)
        allowed = outcomes.get("allowed", 0)
        denied = outcomes.get("denied", 0)
        return {
            "total_events": total,
            "allowed_events": allowed,
            "denied_events": denied,
            "authorization_success_rate": (allowed / total * 100) if total else 0.0,
            "denial_rate": (denied / total * 100) if total else 0.0,
            "retry_failed_events": actions.get("retry_failed", 0),
            "requeue_dead_letter_events": actions.get("requeue_dead_letter", 0),
        }

    def daily_trend(self, organization_id, *, limit=500):
        events = self._events(organization_id, limit)
        trend = defaultdict(lambda: {"total": 0, "allowed": 0, "denied": 0})
        for event in events:
            stamp = event.get("created_at")
            day = self._day(stamp)
            trend[day]["total"] += 1
            outcome = event.get("outcome")
            if outcome in ("allowed", "denied"):
                trend[day][outcome] += 1
        return [
            {"date": day, **values}
            for day, values in sorted(trend.items())
        ]

    @staticmethod
    def _day(value):
        if not value:
            return "unknown"
        if isinstance(value, datetime):
            return value.date().isoformat()
        text = str(value)
        return text[:10] if len(text) >= 10 else text
