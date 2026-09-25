from app.services.notification_admin_access import NotificationAdminAccess
from app.services.notification_admin_integration import NotificationAdminIntegration


def test_owner_and_admin_are_allowed():
    a = NotificationAdminAccess()
    for role in ("owner", "admin"):
        result = a.authorize(actor_user_id="u1", actor_role=role,
                             actor_organization_id="org1", organization_id="org1")
        assert result["role"] == role


def test_non_admin_role_is_rejected():
    a = NotificationAdminAccess()
    try:
        a.authorize(actor_user_id="u1", actor_role="engineer",
                    actor_organization_id="org1", organization_id="org1")
        assert False
    except PermissionError:
        pass


def test_cross_organization_access_is_rejected():
    a = NotificationAdminAccess()
    try:
        a.authorize(actor_user_id="u1", actor_role="admin",
                    actor_organization_id="org1", organization_id="org2")
        assert False
    except PermissionError:
        pass


def test_integration_does_not_render_when_unauthorized():
    calls = []
    integration = NotificationAdminIntegration(
        health_service=object(),
        health_renderer=lambda *args, **kwargs: calls.append(True),
    )
    try:
        integration.render(actor_user_id="u1", actor_role="staff",
                           actor_organization_id="org1", organization_id="org1")
        assert False
    except PermissionError:
        assert calls == []
