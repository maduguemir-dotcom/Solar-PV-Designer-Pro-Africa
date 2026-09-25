"""Authorization boundary for the notification administration workspace."""


class NotificationAdminAccess:
    """Enforce host-authenticated role and organization isolation.

    This adapter deliberately accepts an already authenticated context rather
    than owning authentication. The host application remains responsible for
    establishing identity and session integrity.
    """

    ALLOWED_ROLES = frozenset({"owner", "admin"})

    def authorize(self, *, actor_user_id, actor_role, actor_organization_id, organization_id):
        if not actor_user_id:
            raise PermissionError("authenticated actor is required")
        if not organization_id or actor_organization_id != organization_id:
            raise PermissionError("organization access denied")
        role = str(actor_role or "").strip().lower()
        if role not in self.ALLOWED_ROLES:
            raise PermissionError("notification administration requires owner or admin role")
        return {"actor_user_id": actor_user_id, "organization_id": organization_id, "role": role}
