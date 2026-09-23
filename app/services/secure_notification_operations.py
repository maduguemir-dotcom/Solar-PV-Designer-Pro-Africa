"""Authorized notification operations with durable audit records (Stage 6R)."""
from .notification_security_service import NotificationSecurityService

class SecureNotificationOperations:
    def __init__(self, operations, security, audit):
        self.operations = operations
        self.security = security or NotificationSecurityService()
        self.audit = audit

    def retry_failed(self, *, role, organization_id, actor_organization_id, actor_user_id, limit=25):
        action, target = "retry_failed", "notification_queue"
        self.security.authorize_and_record(role=role, organization_id=organization_id,
            actor_organization_id=actor_organization_id, actor_user_id=actor_user_id,
            action=action, target=target, details=f"limit={limit}")
        count = self.operations.retry_failed(organization_id, limit)
        self.audit.record(organization_id=organization_id, actor_user_id=actor_user_id,
            action=action, target=target, outcome="allowed", details={"count": count, "limit": limit})
        return count

    def requeue_dead_letter(self, *, role, organization_id, actor_organization_id, actor_user_id, limit=25):
        action, target = "requeue_dead_letter", "notification_queue"
        self.security.authorize_and_record(role=role, organization_id=organization_id,
            actor_organization_id=actor_organization_id, actor_user_id=actor_user_id,
            action=action, target=target, details=f"limit={limit}")
        count = self.operations.requeue_dead_letter(organization_id, limit)
        self.audit.record(organization_id=organization_id, actor_user_id=actor_user_id,
            action=action, target=target, outcome="allowed", details={"count": count, "limit": limit})
        return count
