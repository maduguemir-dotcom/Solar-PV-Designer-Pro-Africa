"""Stage 6Z integration tests for notification administration security chain.

These tests use injected fakes for the database and Streamlit surface. They
exercise application service boundaries, not deployment infrastructure.
"""
import sys
import types

import pytest

from app.services.notification_admin_access import NotificationAdminAccess
from app.services.notification_admin_integration import NotificationAdminIntegration
from app.services.notification_admin_security_audit import NotificationAdminSecurityAudit
from app.services.secure_notification_operations import SecureNotificationOperations
from app.services.notification_security_service import NotificationSecurityService
from app.services.notification_audit_history_service import NotificationAuditHistoryService
from app.services.notification_reliability_service import NotificationReliabilityService
from app.services.notification_health_service import NotificationHealthService


class FakeAudit:
    def __init__(self):
        self.events = []

    def record(self, **event):
        self.events.append(dict(event))
        return len(self.events)

    def list_events(self, organization_id, limit=100):
        return [e for e in reversed(self.events)
                if e.get("organization_id") == organization_id][:limit]


class FakeQueueOperations:
    def __init__(self):
        self.calls = []

    def retry_failed(self, organization_id, limit):
        self.calls.append(("retry_failed", organization_id, limit))
        return 2

    def requeue_dead_letter(self, organization_id, limit):
        self.calls.append(("requeue_dead_letter", organization_id, limit))
        return 1


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.rendered = []

    def header(self, value): self.rendered.append(("header", value))
    def caption(self, value): self.rendered.append(("caption", value))
    def info(self, value): self.rendered.append(("info", value))
    def tabs(self, labels):
        self.rendered.append(("tabs", labels))
        return (self, self, self, self)
    def __enter__(self): return self
    def __exit__(self, *args): return False


def test_owner_workspace_render_is_authorized_and_access_is_audited(monkeypatch):
    audit = FakeAudit()
    security_audit = NotificationAdminSecurityAudit(audit)
    fake_st = FakeStreamlit()
    monkeypatch.setitem(sys.modules, "streamlit", fake_st)
    calls = []

    def renderer(*args, **kwargs):
        calls.append((args, kwargs))

    integration = NotificationAdminIntegration(
        health_service=object(), health_renderer=renderer,
        reliability_renderer=lambda org: calls.append(((org,), {})),
        audit_history_renderer=lambda org: calls.append(((org,), {})),
        recovery_renderer=lambda org: calls.append(((org,), {})),
        security_audit=security_audit,
    )
    integration.render(actor_user_id="u-owner", actor_role="owner",
                       actor_organization_id="org-a", organization_id="org-a")

    assert any(item[0] == "header" and item[1] == "Notification Operations"
               for item in fake_st.rendered)
    assert len(calls) == 4
    assert audit.events[0]["outcome"] == "allowed"
    assert audit.events[0]["organization_id"] == "org-a"
    assert audit.events[0]["action"] == "notification_admin_access"


def test_staff_is_rejected_before_any_workspace_render_and_audited():
    audit = FakeAudit()
    access = NotificationAdminAccess(security_audit=NotificationAdminSecurityAudit(audit))
    integration = NotificationAdminIntegration(
        health_service=object(), health_renderer=lambda *a, **k: pytest.fail("rendered before authorization"),
        access=access,
    )
    with pytest.raises(PermissionError):
        integration.render(actor_user_id="u-staff", actor_role="staff",
                           actor_organization_id="org-a", organization_id="org-a")
    assert audit.events[-1]["outcome"] == "denied"
    assert audit.events[-1]["details"]["actor_role"] == "staff"


def test_cross_organization_access_is_denied_and_audited():
    audit = FakeAudit()
    access = NotificationAdminAccess(security_audit=NotificationAdminSecurityAudit(audit))
    with pytest.raises(PermissionError):
        access.authorize(actor_user_id="u-admin", actor_role="admin",
                         actor_organization_id="org-a", organization_id="org-b")
    event = audit.events[-1]
    assert event["outcome"] == "denied"
    assert event["organization_id"] == "org-b"
    assert event["details"]["actor_organization_id"] == "org-a"
    assert event["details"]["requested_organization_id"] == "org-b"


def test_secure_recovery_authorizes_org_scope_and_audits_success():
    audit = FakeAudit()
    operations = FakeQueueOperations()
    secure = SecureNotificationOperations(operations, NotificationSecurityService(), audit)
    count = secure.retry_failed(role="admin", organization_id="org-a",
                                actor_organization_id="org-a", actor_user_id="u-admin", limit=10)
    assert count == 2
    assert operations.calls == [("retry_failed", "org-a", 10)]
    assert audit.events[-1]["outcome"] == "allowed"
    assert audit.events[-1]["action"] == "retry_failed"
    assert audit.events[-1]["details"]["count"] == 2


def test_secure_recovery_rejects_cross_org_without_calling_queue_and_audits_denial():
    audit = FakeAudit()
    operations = FakeQueueOperations()
    secure = SecureNotificationOperations(operations, NotificationSecurityService(), audit)
    with pytest.raises(PermissionError):
        secure.requeue_dead_letter(role="admin", organization_id="org-b",
                                   actor_organization_id="org-a", actor_user_id="u-admin")
    assert operations.calls == []
    assert audit.events[-1]["outcome"] == "denied"
    assert audit.events[-1]["action"] == "requeue_dead_letter"


def test_history_reliability_and_health_queries_are_organization_scoped():
    audit = FakeAudit()
    audit.record(organization_id="org-a", actor_user_id="u1", action="retry_failed",
                 target="queue", outcome="allowed", details={})
    audit.record(organization_id="org-b", actor_user_id="u2", action="retry_failed",
                 target="queue", outcome="denied", details={})
    history = NotificationAuditHistoryService(audit)
    assert len(history.list_history("org-a")) == 1
    assert history.list_history("org-a")[0]["organization_id"] == "org-a"

    reliability = NotificationReliabilityService(audit)
    health = NotificationHealthService(reliability, audit)
    snapshot = health.snapshot("org-a")
    assert snapshot["organization_id"] == "org-a"
    assert snapshot["audit_events_available"] == 1
    assert snapshot["latest_event"]["organization_id"] == "org-a"


def test_audit_history_rejects_missing_org_and_invalid_limit():
    history = NotificationAuditHistoryService(FakeAudit())
    with pytest.raises(ValueError):
        history.list_history("")
    with pytest.raises(ValueError):
        history.list_history("org-a", limit=501)
