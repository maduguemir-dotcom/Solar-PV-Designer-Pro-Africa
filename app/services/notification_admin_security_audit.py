"""Audit adapter for notification administration access decisions."""


class NotificationAdminSecurityAudit:
    """Record administration access decisions through an injected audit service.

    The durable audit implementation is supplied by the host application.
    This adapter deliberately has no database dependency of its own.
    """

    def __init__(self, audit_service):
        if audit_service is None or not callable(getattr(audit_service, "record", None)):
            raise TypeError("audit_service with callable record() is required")
        self.audit_service = audit_service

    def record_access(self, *, actor_user_id, actor_role, actor_organization_id,
                      organization_id, outcome, details=None):
        self.audit_service.record(
            organization_id=organization_id or actor_organization_id,
            actor_user_id=actor_user_id,
            action="notification_admin_access",
            target="notification_operations_workspace",
            outcome=outcome,
            details={
                "actor_role": actor_role,
                "actor_organization_id": actor_organization_id,
                "requested_organization_id": organization_id,
                **(details or {}),
            },
        )
