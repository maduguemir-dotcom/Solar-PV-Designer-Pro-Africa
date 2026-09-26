"""Composition and authorization boundary for notification administration."""

from app.services.notification_admin_access import NotificationAdminAccess


class NotificationAdminIntegration:
    """Dependency-injection boundary for the host administration page."""

    def __init__(self, *, health_service, health_renderer, access=None,
                 reliability_renderer=None, audit_history_renderer=None,
                 recovery_renderer=None, security_audit=None):
        self.health_service = health_service
        self.health_renderer = health_renderer
        self.access = access or NotificationAdminAccess(security_audit=security_audit)
        self.reliability_renderer = reliability_renderer
        self.audit_history_renderer = audit_history_renderer
        self.recovery_renderer = recovery_renderer

    def render(self, *, actor_user_id, actor_role, actor_organization_id, organization_id):
        actor = self.access.authorize(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            actor_organization_id=actor_organization_id,
            organization_id=organization_id,
        )
        from app.ui.notification_admin_workspace import render_notification_admin_workspace
        return render_notification_admin_workspace(
            organization_id=organization_id,
            actor=actor,
            health_renderer=self.health_renderer,
            reliability_renderer=self.reliability_renderer,
            audit_history_renderer=self.audit_history_renderer,
            recovery_renderer=self.recovery_renderer,
            health_service=self.health_service,
        )
