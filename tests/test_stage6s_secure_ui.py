import sys
import types

import pytest

from app.ui.notification_operations import render_notification_operations

# Stage 6Q security module is supplied by the cumulative project; inject a
# minimal compatible class so this Stage-Only test remains independently runnable.
security_module = types.ModuleType("app.services.notification_security_service")
class NotificationSecurityService: pass
security_module.NotificationSecurityService = NotificationSecurityService
sys.modules["app.services.notification_security_service"] = security_module

from app.services.secure_notification_operations import SecureNotificationOperations


class FakeColumn:
    def metric(self, *_args):
        pass


class FakeStreamlit:
    def __init__(self, buttons=(False, False)):
        self.buttons = list(buttons)
        self.messages = []

    def subheader(self, value):
        self.messages.append(("subheader", value))

    def columns(self, n):
        return [FakeColumn() for _ in range(n)]

    def metric(self, *args):
        self.messages.append(("metric", args))

    def info(self, value): self.messages.append(("info", value))
    def warning(self, value): self.messages.append(("warning", value))
    def error(self, value): self.messages.append(("error", value))
    def success(self, value): self.messages.append(("success", value))

    def button(self, _label):
        return self.buttons.pop(0)


class MetricsService:
    def metrics(self, _org):
        return {"queued": 1, "processing": 0, "sent": 3,
                "failed": 2, "dead_letter": 1, "attention_required": 3}


class SecureFake:
    def __init__(self):
        self.calls = []

    def retry_failed(self, **kwargs):
        self.calls.append(("retry", kwargs)); return 2

    def requeue_dead_letter(self, **kwargs):
        self.calls.append(("dead", kwargs)); return 1


def install_fake_streamlit(fake):
    sys.modules["streamlit"] = fake


def test_ui_routes_recovery_actions_through_secure_service(monkeypatch):
    fake = FakeStreamlit(buttons=(True, True))
    install_fake_streamlit(fake)
    secure = SecureFake()
    actor = {"role": "admin", "user_id": "u1", "organization_id": "org1"}

    render_notification_operations(MetricsService(), "org1", actor=actor,
                                   secure_service=secure)

    assert [name for name, _ in secure.calls] == ["retry", "dead"]
    assert secure.calls[0][1]["actor_user_id"] == "u1"
    assert secure.calls[0][1]["actor_organization_id"] == "org1"


def test_ui_blocks_missing_identity(monkeypatch):
    fake = FakeStreamlit()
    install_fake_streamlit(fake)
    secure = SecureFake()

    render_notification_operations(MetricsService(), "org1", secure_service=secure)

    assert secure.calls == []
    assert any(kind == "warning" for kind, _ in fake.messages)


def test_secure_operations_deny_cross_org_and_create_durable_audit():
    class Ops:
        def retry_failed(self, *_args):
            raise AssertionError("operation must not execute")

    class Security:
        def authorize_and_record(self, **_kwargs):
            raise PermissionError("denied")

    class Audit:
        def __init__(self): self.events = []
        def record(self, **kwargs): self.events.append(kwargs)

    audit = Audit()
    secure = SecureNotificationOperations(Ops(), Security(), audit)

    with pytest.raises(PermissionError):
        secure.retry_failed(role="staff", organization_id="org1",
                            actor_organization_id="org2", actor_user_id="u2")

    assert audit.events[-1]["outcome"] == "denied"
    assert audit.events[-1]["organization_id"] == "org1"
