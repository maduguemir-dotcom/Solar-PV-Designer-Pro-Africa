"""Stage 6V notification health aggregation.

This service composes existing organization-scoped operational services into a
single read-only health snapshot. It does not execute recovery operations.
"""


class NotificationHealthService:
    def __init__(self, reliability_service, audit_service):
        self.reliability_service = reliability_service
        self.audit_service = audit_service

    def snapshot(self, organization_id, *, limit=500):
        if not organization_id:
            raise ValueError("organization_id is required")
        summary = self.reliability_service.summarize(organization_id, limit=limit)
        events = self.audit_service.list_events(organization_id, limit=limit)
        latest = events[0] if events else None
        return {
            "organization_id": organization_id,
            "summary": summary,
            "latest_event": latest,
            "audit_events_available": len(events),
        }
