"""Organization-scoped notification audit history (Stage 6T)."""


class NotificationAuditHistoryService:
    """Read-only presentation/query boundary over the durable audit service."""

    def __init__(self, audit_service):
        self.audit_service = audit_service

    def list_history(self, organization_id, *, outcome=None, action=None, limit=100):
        if not organization_id:
            raise ValueError("organization_id is required")
        if limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500")
        events = self.audit_service.list_events(organization_id, limit=limit)
        if outcome:
            events = [e for e in events if e.get("outcome") == outcome]
        if action:
            events = [e for e in events if e.get("action") == action]
        return events
