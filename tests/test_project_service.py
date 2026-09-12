from pathlib import Path

from app.platform.database import PlatformDatabase
from app.services.project_service import ProjectService


def test_full_project_design_workflow(tmp_path: Path):
    service = ProjectService(PlatformDatabase(tmp_path / "platform.db"))
    onboarding = service.onboard_user(
        "Engineer@example.com", "Engr. Test User", "Test Solar Company"
    )
    org_id = onboarding["organization_id"]

    customer_project = service.create_customer_project(
        org_id,
        "Sample Customer",
        "5 kWh/day Solar Home",
        customer_email="customer@example.com",
        location="Kampala",
    )
    design_id = service.create_design(customer_project["project_id"], "Professional Design")
    equipment_id = service.attach_equipment(
        design_id, "Solar Panel", "prod_panel_001", 10,
        {"rated_power_w": 550, "vmp_v": 41.5, "voc_v": 49.5},
    )
    result_id = service.save_engineering_result(
        design_id, {"pv_kwp": 5.5, "status": "PASS WITH WARNINGS"}, 86.0
    )
    usage_id = service.record_design_usage(org_id)

    assert service.repository.get_one("users", onboarding["user_id"])["email"] == "engineer@example.com"
    assert service.repository.get_one("organizations", org_id)["name"] == "Test Solar Company"
    assert service.repository.get_one("projects", customer_project["project_id"])["customer_id"] == customer_project["customer_id"]
    assert service.repository.get_one("designs", design_id)["version"] == 1
    assert service.repository.get_one("design_equipment", equipment_id)["product_id"] == "prod_panel_001"
    assert service.repository.get_one("design_results", result_id)["quality_score"] == 86.0
    assert service.repository.get_one("usage_records", usage_id)["metric"] == "design_runs"
