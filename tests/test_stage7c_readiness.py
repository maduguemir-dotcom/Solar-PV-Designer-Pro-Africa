from pathlib import Path

from app.services.notification_integration_readiness import NotificationIntegrationReadiness


def test_readiness_fails_when_entrypoint_is_not_wired(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app/main.py").write_text("import streamlit as st\nst.title('App')\n", encoding="utf-8")
    result = NotificationIntegrationReadiness(tmp_path).run(required_files=())
    assert result["ready"] is False
    checks = {item["name"]: item for item in result["checks"]}
    assert checks["application_entrypoint"]["passed"] is True
    assert checks["admin_workspace_wiring"]["passed"] is False


def test_readiness_detects_explicit_workspace_marker(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app/main.py").write_text(
        "from app.ui.notification_admin_workspace import render_notification_admin_workspace\n",
        encoding="utf-8",
    )
    result = NotificationIntegrationReadiness(tmp_path).run(required_files=())
    assert result["ready"] is True
    assert result["failed_count"] == 0


def test_readiness_reports_missing_required_modules(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app/main.py").write_text(
        "from app.ui.notification_admin_workspace import render_notification_admin_workspace\n",
        encoding="utf-8",
    )
    result = NotificationIntegrationReadiness(tmp_path).run(
        required_files=("app/services/not_present.py",)
    )
    assert result["ready"] is False
    required = next(c for c in result["checks"] if c["name"] == "required_modules")
    assert "app/services/not_present.py" in required["detail"]
