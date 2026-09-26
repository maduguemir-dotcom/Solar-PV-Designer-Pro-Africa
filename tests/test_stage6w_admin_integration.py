from app.services.notification_admin_integration import NotificationAdminIntegration


def _render_args(integration, **overrides):
    args = {
        "actor_user_id": "u1",
        "actor_role": "admin",
        "actor_organization_id": "org-123",
        "organization_id": "org-123",
    }
    args.update(overrides)
    return integration.render(**args)


def test_integration_requires_organization_id():
    integration = NotificationAdminIntegration(
        health_service=object(),
        health_renderer=lambda *args, **kwargs: None,
    )
    try:
        _render_args(integration, organization_id="")
    except ValueError as exc:
        assert "organization_id" in str(exc)
    except PermissionError as exc:
        # Authorization rejects a missing organization before rendering.
        assert "organization" in str(exc).lower()
    else:
        raise AssertionError("missing organization_id must be rejected")


def test_integration_passes_scoped_dependencies(monkeypatch):
    captured = {}

    def fake_renderer(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        "app.ui.notification_admin_workspace.render_notification_admin_workspace",
        fake_renderer,
    )
    health_service = object()
    health_renderer = lambda *args, **kwargs: None
    integration = NotificationAdminIntegration(
        health_service=health_service,
        health_renderer=health_renderer,
    )
    _render_args(integration)
    assert captured["organization_id"] == "org-123"
    assert captured["health_service"] is health_service
    assert captured["health_renderer"] is health_renderer


def test_workspace_rejects_non_callable_health_renderer():
    from app.ui.notification_admin_workspace import render_notification_admin_workspace

    try:
        render_notification_admin_workspace(
            organization_id="org-123",
            actor={"actor_user_id": "u1", "organization_id": "org-123", "role": "admin"},
            health_renderer=None,
        )
    except TypeError as exc:
        assert "health_renderer" in str(exc)
    else:
        raise AssertionError("non-callable health_renderer must be rejected")
