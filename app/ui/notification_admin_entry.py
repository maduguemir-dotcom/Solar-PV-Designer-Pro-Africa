"""Host-application entry point for the secured notification admin workspace.

The authenticated identity comes from the existing Stage 5A session. The role is
re-resolved from the selected organization's membership in the platform database,
so changing the organization selector cannot reuse a role from another workspace.
"""


def _membership_for_organization(memberships, organization_id):
    """Return the user's membership for this organization, or None."""
    if not organization_id:
        return None
    return next(
        (membership for membership in memberships
         if membership.get("id") == organization_id),
        None,
    )


def render_notification_admin_page():
    import streamlit as st

    from app.auth.ui import current_identity, current_organization_id
    from app.platform.database import PlatformDatabase
    from app.platform.repositories import PlatformRepository
    from app.services.durable_audit_service import DurableAuditService
    from app.services.notification_admin_access import NotificationAdminAccess
    from app.services.notification_admin_integration import NotificationAdminIntegration
    from app.services.notification_admin_security_audit import NotificationAdminSecurityAudit
    from app.services.notification_audit_analytics_service import (
        NotificationReliabilityService as AuditAnalyticsService,
    )
    from app.services.notification_audit_history_service import NotificationAuditHistoryService
    from app.services.notification_health_service import NotificationHealthService
    from app.services.notification_operations_service import NotificationOperationsService
    from app.services.notification_security_service import NotificationSecurityService
    from app.services.secure_notification_operations import SecureNotificationOperations
    from app.ui.notification_audit_history import render_notification_audit_history
    from app.ui.notification_health_dashboard import render_notification_health_dashboard
    from app.ui.notification_operations import render_notification_operations
    from app.ui.notification_reliability import render_notification_reliability

    identity = current_identity()
    organization_id = current_organization_id()
    if not isinstance(identity, dict) or not identity.get("user_id"):
        st.error("Please sign in before opening notification administration.")
        return
    if not organization_id:
        st.error("Select an organization before opening notification administration.")
        return

    db = PlatformDatabase()
    db.initialize()
    repository = PlatformRepository(db)
    memberships = repository.organizations_for_user(identity["user_id"])
    membership = _membership_for_organization(memberships, organization_id)
    if membership is None:
        st.error("Access denied: you are not a member of the selected organization.")
        return

    # Use the role attached to the selected organization's persisted membership,
    # not a role supplied by a UI control or a stale session organization.
    actor = {
        "user_id": identity["user_id"],
        "role": membership.get("member_role"),
        "organization_id": organization_id,
    }

    audit = DurableAuditService(db)
    audit_adapter = NotificationAdminSecurityAudit(audit)
    audit_analytics = AuditAnalyticsService(audit)
    history_service = NotificationAuditHistoryService(audit)
    queue_operations = NotificationOperationsService(db)
    secure_operations = SecureNotificationOperations(
        operations=queue_operations,
        security=NotificationSecurityService(),
        audit=audit,
    )
    health_service = NotificationHealthService(audit_analytics, audit)

    # The health panel has its own compact summary. Other views are rendered in
    # separate tabs to avoid duplicate controls and duplicate database queries.
    def render_health(service, org_id, **_nested_renderers):
        return render_notification_health_dashboard(service, org_id)

    def render_history(org_id, *_optional_limit):
        return render_notification_audit_history(history_service, org_id)

    def render_reliability(org_id, *_optional_limit):
        return render_notification_reliability(audit_analytics, org_id)

    def render_recovery(org_id, *_optional_args):
        return render_notification_operations(
            queue_operations,
            org_id,
            actor=actor,
            secure_service=secure_operations,
            audit_history_service=history_service,
        )

    integration = NotificationAdminIntegration(
        health_service=health_service,
        health_renderer=render_health,
        access=NotificationAdminAccess(security_audit=audit_adapter),
        reliability_renderer=render_reliability,
        audit_history_renderer=render_history,
        recovery_renderer=render_recovery,
    )

    try:
        integration.render(
            actor_user_id=identity["user_id"],
            actor_role=actor["role"],
            actor_organization_id=actor["organization_id"],
            organization_id=organization_id,
        )
    except PermissionError:
        st.error("Access denied. Notification administration requires the owner or admin role for this organization.")
