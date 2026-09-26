"""Read-only readiness checks for notification administration integration.

This module checks repository wiring without importing Streamlit or opening the DB.
It is a pre-deployment gate, not a substitute for running the full application.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = (
    "app/services/durable_audit_service.py",
    "app/services/secure_notification_operations.py",
    "app/services/notification_reliability_service.py",
    "app/services/notification_audit_analytics_service.py",
    "app/services/notification_audit_history_service.py",
    "app/services/notification_health_service.py",
    "app/services/notification_admin_access.py",
    "app/services/notification_admin_security_audit.py",
    "app/services/notification_admin_integration.py",
    "app/ui/notification_operations.py",
    "app/ui/notification_audit_history.py",
    "app/ui/notification_reliability.py",
    "app/ui/notification_health_dashboard.py",
    "app/ui/notification_admin_workspace.py",
)

# The host app should explicitly call the admin workspace from its actual entry point.
ENTRYPOINT_CANDIDATES = ("app/main.py", "app.py", "main.py")
INTEGRATION_MARKERS = (
    "notification_admin_workspace",
    "render_notification_admin",
    "NotificationAdminIntegration",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


class NotificationIntegrationReadiness:
    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()

    def run(self, required_files: Iterable[str] = REQUIRED_FILES) -> dict:
        checks: list[Check] = []
        missing = [rel for rel in required_files if not (self.root / rel).is_file()]
        checks.append(Check(
            "required_modules",
            not missing,
            "All required notification modules are present." if not missing
            else "Missing files: " + ", ".join(missing),
        ))

        entrypoint = next((self.root / rel for rel in ENTRYPOINT_CANDIDATES
                           if (self.root / rel).is_file()), None)
        if entrypoint is None:
            checks.append(Check("application_entrypoint", False,
                                "No recognized application entry point found."))
            checks.append(Check("admin_workspace_wiring", False,
                                "Cannot verify workspace wiring without an entry point."))
        else:
            checks.append(Check("application_entrypoint", True,
                                f"Found {entrypoint.relative_to(self.root).as_posix()}"))
            try:
                source = entrypoint.read_text(encoding="utf-8")
            except OSError as exc:
                checks.append(Check("admin_workspace_wiring", False,
                                    f"Could not read entry point: {exc}"))
            else:
                markers = [marker for marker in INTEGRATION_MARKERS if marker in source]
                checks.append(Check(
                    "admin_workspace_wiring", bool(markers),
                    "Found integration marker(s): " + ", ".join(markers) if markers
                    else "No notification administration integration marker found in the entry point.",
                ))

        failed = [asdict(c) for c in checks if not c.passed]
        return {
            "ready": not failed,
            "checks": [asdict(c) for c in checks],
            "failed_count": len(failed),
            "summary": "Ready for the next validation layer." if not failed
                       else "Not production-ready: resolve failed checks before release.",
        }
