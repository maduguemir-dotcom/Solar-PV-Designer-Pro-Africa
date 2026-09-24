"""Authorized notification operations with durable audit records (Stage 6S)."""
from .notification_security_service import NotificationSecurityService


class SecureNotificationOperations:
    """Authorization boundary for notification recovery actions.

    Every attempted action is passed through the security service. Successful
    and denied attempts are also written to the durable audit service so the
    operational dashboard cannot become an unaudited administrative backdoor.
    """

    def __init__(self, operations, security, audit):
        self.operations = operations
        self.security = security or NotificationSecurityService()
        self.audit = audit

    def _authorize(self, *, role, organization_id, actor_organization_id,
                   actor_user_id, action, target, limit):
        try:
            self.security.authorize_and_record(
                role=role,
                organization_id=organization_id,
                actor_organization_id=actor_organization_id,
                actor_user_id=actor_user_id,
                action=action,
                target=target,
                details=f"limit={limit}",
            )
        except PermissionError:
            self.audit.record(
                organization_id=organization_id or "unknown",
                actor_user_id=actor_user_id,
                action=action,
                target=target,
                outcome="denied",
                details={"limit": limit},
            )
            raise

    def retry_failed(self, *, role, organization_id, actor_organization_id,
                     actor_user_id, limit=25):
        action, target = "retry_failed", "notification_queue"
        self._authorize(
            role=role, organization_id=organization_id,
            actor_organization_id=actor_organization_id,
            actor_user_id=actor_user_id, action=action, target=target,
            limit=limit,
        )
        count = self.operations.retry_failed(organization_id, limit)
        self.audit.record(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            target=target,
            outcome="allowed",
            details={"count": count, "limit": limit},
        )
        return count

    def requeue_dead_letter(self, *, role, organization_id, actor_organization_id,
                            actor_user_id, limit=25):
        action, target = "requeue_dead_letter", "notification_queue"
        self._authorize(
            role=role, organization_id=organization_id,
            actor_organization_id=actor_organization_id,
            actor_user_id=actor_user_id, action=action, target=target,
            limit=limit,
        )
        count = self.operations.requeue_dead_letter(organization_id, limit)
        self.audit.record(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            target=target,
            outcome="allowed",
            details={"count": count, "limit": limit},
        )
        return count
