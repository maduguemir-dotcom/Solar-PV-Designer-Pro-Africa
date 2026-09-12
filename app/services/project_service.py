"""Application service for the Stage 4A project/business workflow."""
from __future__ import annotations

from typing import Any, Optional

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository


class ProjectService:
    """Coordinates users → organizations → customers → projects → designs."""

    def __init__(self, database: Optional[PlatformDatabase] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)

    def onboard_user(self, email: str, full_name: str = "", organization_name: Optional[str] = None) -> dict[str, str]:
        user_id = self.repository.create_user(email=email, full_name=full_name)
        result = {"user_id": user_id}
        if organization_name:
            result["organization_id"] = self.repository.create_organization(organization_name, user_id)
        return result

    def create_customer_project(
        self,
        organization_id: str,
        customer_name: str,
        project_name: str,
        *,
        customer_email: str = "",
        customer_phone: str = "",
        location: str = "",
        notes: str = "",
    ) -> dict[str, str]:
        customer_id = self.repository.create_customer(
            organization_id, customer_name, customer_email, customer_phone
        )
        project_id = self.repository.create_project(
            organization_id, project_name, customer_id, location, notes
        )
        return {"customer_id": customer_id, "project_id": project_id}

    def create_design(self, project_id: str, name: str, engine_version: str = "v4") -> str:
        return self.repository.create_design(project_id, name, engine_version)

    def attach_equipment(self, design_id: str, equipment_type: str, product_id: str, quantity: int = 1, snapshot: Optional[dict[str, Any]] = None) -> str:
        return self.repository.add_design_equipment(design_id, equipment_type, product_id, quantity, snapshot)

    def save_engineering_result(self, design_id: str, result: dict[str, Any], quality_score: Optional[float] = None) -> str:
        return self.repository.save_design_result(design_id, "engineering", result, quality_score)

    def record_design_usage(self, organization_id: str, metric: str = "design_runs", quantity: int = 1) -> str:
        return self.repository.record_usage(organization_id, metric, quantity)
