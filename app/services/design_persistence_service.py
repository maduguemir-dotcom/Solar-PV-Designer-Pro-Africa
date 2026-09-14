"""Stage 4C service for saving and loading professional design history."""
from __future__ import annotations
from typing import Any, Mapping, Optional
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.subscription_service import SubscriptionService

class DesignPersistenceService:
    def __init__(self, database: Optional[PlatformDatabase] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)
        self.subscription = SubscriptionService(self.database)

    def save_professional_design(self, *, organization_id: str, project_id: str,
                                 result: Mapping[str, Any], equipment_selection: Mapping[str, Any] | None = None,
                                 design_id: str | None = None, design_name: str | None = None,
                                 engine_version: str = "v4") -> dict[str, Any]:
        project = self.repository.get_one("projects", project_id)
        if not project or project.get("organization_id") != organization_id:
            raise ValueError("Project does not belong to the selected organization.")
        is_new_design = design_id is None
        # Check entitlement before creating anything so a rejected save leaves
        # no empty design version behind.
        if is_new_design:
            self.subscription.require_limit(organization_id, "professional_designs_saved")

        if design_id:
            design = self.repository.get_one("designs", design_id)
            if not design or design.get("project_id") != project_id:
                raise ValueError("Selected design does not belong to the selected project.")
        else:
            design_id = self.repository.create_design(project_id, design_name or str(result.get("project_name") or "Professional Engineering Design"), engine_version)
            design = self.repository.get_one("designs", design_id)

        selected = (equipment_selection or {}).get("selected", {}) if isinstance(equipment_selection, Mapping) else {}
        equipment_ids = []
        roles = {"pv_module":"PV Module", "battery":"Battery", "inverter":"Inverter", "charge_controller":"Charge Controller"}
        for role, label in roles.items():
            item = selected.get(role)
            if not isinstance(item, Mapping):
                continue
            product = item.get("product", {})
            pid = str(product.get("id") or item.get("validation", {}).get("product", {}).get("product_id") or "")
            if not pid:
                continue
            snapshot = {"product": product, "role": role, "validation": item.get("validation", {})}
            equipment_ids.append(self.repository.add_design_equipment(design_id, label, pid, 1, snapshot))
        result_id = self.repository.save_design_result(design_id, "engineering", dict(result), result.get("design_quality_score"))
        self.repository.update_record("designs", design_id, {"status": "completed", "engine_version": engine_version})
        if is_new_design:
            self.repository.record_usage(organization_id, "professional_designs_saved", 1)
        return {"design_id": design_id, "result_id": result_id, "equipment_ids": equipment_ids, "version": design.get("version", 1) if design else 1}

    def design_history(self, project_id: str) -> list[dict[str, Any]]:
        return self.repository.list_records("designs", "project_id=?", (project_id,))

    def load_design_result(self, design_id: str) -> dict[str, Any] | None:
        rows = self.repository.list_records("design_results", "design_id=? AND result_type=?", (design_id, "engineering"))
        if not rows:
            return None
        import json
        latest = rows[0]
        try:
            latest["result"] = json.loads(latest["result_json"])
        except (TypeError, ValueError):
            latest["result"] = {}
        return latest
