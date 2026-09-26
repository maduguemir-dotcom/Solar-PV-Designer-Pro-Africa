from app.services.notification_admin_security_audit import NotificationAdminSecurityAudit
from app.services.notification_admin_access import NotificationAdminAccess
from app.services.notification_admin_integration import NotificationAdminIntegration


class FakeAudit:
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


def test_allowed_access_is_durably_audited():
    audit = FakeAudit()
    access = NotificationAdminAccess(security_audit=NotificationAdminSecurityAudit(audit))
    result = access.authorize(actor_user_id="u1", actor_role="admin",
                              actor_organization_id="org1", organization_id="org1")
    assert result["role"] == "admin"
    assert audit.events[0]["outcome"] == "allowed"
    assert audit.events[0]["action"] == "notification_admin_access"


def test_denied_access_is_audited_before_exception():
    audit = FakeAudit()
    access = NotificationAdminAccess(security_audit=NotificationAdminSecurityAudit(audit))
    try:
        access.authorize(actor_user_id="u1", actor_role="staff",
                         actor_organization_id="org1", organization_id="org1")
        assert False
    except PermissionError:
        pass
    assert audit.events[0]["outcome"] == "denied"
    assert audit.events[0]["details"]["reason"]


def test_cross_org_denial_is_audited():
    audit = FakeAudit()
    access = NotificationAdminAccess(security_audit=NotificationAdminSecurityAudit(audit))
    try:
        access.authorize(actor_user_id="u1", actor_role="admin",
                         actor_organization_id="org1", organization_id="org2")
        assert False
    except PermissionError:
        pass
    event = audit.events[0]
    assert event["organization_id"] == "org2"
    assert event["details"]["actor_organization_id"] == "org1"


def test_integration_uses_injected_security_audit():
    audit = FakeAudit()
    integration = NotificationAdminIntegration(
        health_service=object(),
        health_renderer=lambda *args, **kwargs: None,
        security_audit=NotificationAdminSecurityAudit(audit),
    )
    actor = integration.access.authorize(actor_user_id="u1", actor_role="owner",
                                         actor_organization_id="org1", organization_id="org1")
    assert actor["role"] == "owner"
    assert audit.events[0]["outcome"] == "allowed"
