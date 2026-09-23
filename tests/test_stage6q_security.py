from app.services.notification_security_service import NotificationSecurityService

def test_admin_same_org_is_allowed_and_audited():
    events = []
    service = NotificationSecurityService(events.append)
    event = service.authorize_and_record(role="admin", organization_id="org1",
        actor_organization_id="org1", actor_user_id="u1", action="retry", target="n1")
    assert event.outcome == "allowed"
    assert events[0].action == "retry"

def test_cross_org_is_denied_and_audited():
    events = []
    service = NotificationSecurityService(events.append)
    try:
        service.authorize_and_record(role="admin", organization_id="org1",
            actor_organization_id="org2", actor_user_id="u1", action="requeue", target="n1")
    except PermissionError:
        pass
    else:
        raise AssertionError("Expected PermissionError")
    assert events[0].outcome == "denied"
