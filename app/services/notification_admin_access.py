"""Authorization and security-audit boundary for notification administration."""


class NotificationAdminAccess:
    """Enforce authenticated role/org access and optionally audit every decision."""

    ALLOWED_ROLES = frozenset({"owner", "admin"})

    def __init__(self, *, security_audit=None):
        self.security_audit = security_audit

    def _audit(self, **kwargs):
        if self.security_audit:
            self.security_audit.record_access(**kwargs)

    def authorize(self, *, actor_user_id, actor_role, actor_organization_id, organization_id):
        role = str(actor_role or "").strip().lower()
        try:
            if not actor_user_id:
                raise PermissionError("authenticated actor is required")
            if not organization_id or actor_organization_id != organization_id:
                raise PermissionError("organization access denied")
            if role not in self.ALLOWED_ROLES:
                raise PermissionError("notification administration requires owner or admin role")
        except PermissionError as exc:
            self._audit(
                actor_user_id=actor_user_id,
                actor_role=role,
                actor_organization_id=actor_organization_id,
                organization_id=organization_id,
                outcome="denied",
                details={"reason": str(exc)},
            )
            raise

        result = {"actor_user_id": actor_user_id, "organization_id": organization_id, "role": role}
        self._audit(
            actor_user_id=actor_user_id,
            actor_role=role,
            actor_organization_id=actor_organization_id,
            organization_id=organization_id,
            outcome="allowed",
        )
        return result
