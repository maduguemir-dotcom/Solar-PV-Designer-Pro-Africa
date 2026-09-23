"""Authorization and audit helpers for notification operations (Stage 6Q)."""
from dataclasses import dataclass
from datetime import datetime, timezone

ALLOWED_ROLES = {"owner", "admin"}

@dataclass(frozen=True)
class AuditEvent:
    organization_id: str
    actor_user_id: str
    action: str
    target: str
    outcome: str
    created_at: str
    details: str = ""

class NotificationSecurityService:
    def __init__(self, audit_sink=None):
        self.audit_sink = audit_sink

    def authorize(self, *, role, organization_id, actor_organization_id, permission="manage_notifications"):
        allowed = role in ALLOWED_ROLES and bool(organization_id) and organization_id == actor_organization_id
        if not allowed:
            raise PermissionError("Insufficient role or organization scope for notification administration")
        return True

    def record(self, *, organization_id, actor_user_id, action, target, outcome, details=""):
        event = AuditEvent(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            target=target,
            outcome=outcome,
            created_at=datetime.now(timezone.utc).isoformat(),
            details=details,
        )
        if self.audit_sink:
            self.audit_sink(event)
        return event

    def authorize_and_record(self, *, role, organization_id, actor_organization_id,
                             actor_user_id, action, target, details=""):
        try:
            self.authorize(role=role, organization_id=organization_id,
                           actor_organization_id=actor_organization_id)
        except PermissionError:
            self.record(organization_id=organization_id or "unknown",
                        actor_user_id=actor_user_id, action=action, target=target,
                        outcome="denied", details=details)
            raise
        return self.record(organization_id=organization_id, actor_user_id=actor_user_id,
                           action=action, target=target, outcome="allowed", details=details)
