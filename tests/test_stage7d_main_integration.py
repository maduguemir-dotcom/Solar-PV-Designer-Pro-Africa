from pathlib import Path

from app.ui.notification_admin_entry import _membership_for_organization


def test_membership_is_resolved_for_selected_organization():
    memberships = [
        {"id": "org-a", "member_role": "owner"},
        {"id": "org-b", "member_role": "staff"},
    ]
    assert _membership_for_organization(memberships, "org-b")["member_role"] == "staff"
    assert _membership_for_organization(memberships, "org-c") is None


def test_main_app_contains_notification_admin_navigation_and_route():
    main_path = Path(__file__).parents[1] / "app" / "main.py"
    source = main_path.read_text(encoding="utf-8")
    assert '"🛡️ Notification Administration"' in source
    assert "render_notification_admin_page()" in source
    assert "from ui.notification_admin_entry import render_notification_admin_page" in source


def test_durable_audit_returns_mapping_rows():
    service_path = Path(__file__).parents[1] / "app" / "services" / "durable_audit_service.py"
    source = service_path.read_text(encoding="utf-8")
    assert "return [dict(row) for row in rows]" in source


def test_durable_audit_events_are_dicts(tmp_path):
    import sqlite3

    from app.services.durable_audit_service import DurableAuditService

    class SQLiteDatabase:
        def __init__(self, path):
            self.path = path

        def connect(self):
            connection = sqlite3.connect(self.path)
            connection.row_factory = sqlite3.Row
            return connection

    audit = DurableAuditService(SQLiteDatabase(tmp_path / "audit.db"))
    audit.record(
        organization_id="org-a", actor_user_id="user-a",
        action="notification_admin_access", target="workspace",
        outcome="allowed", details={"source": "test"},
    )
    events = audit.list_events("org-a")
    assert isinstance(events[0], dict)
    assert events[0]["organization_id"] == "org-a"
    assert events[0]["outcome"] == "allowed"
