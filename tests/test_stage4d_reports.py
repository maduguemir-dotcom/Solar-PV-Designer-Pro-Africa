from pathlib import Path
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.design_persistence_service import DesignPersistenceService
from app.services.professional_report_service import ProfessionalReportService


def test_generate_and_register_professional_report(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user = repo.create_user("report@example.com", "Report User")
    org = repo.create_organization("Report Solar", user)
    project = repo.create_project(org, "Clinic Project", location="Kampala")
    saved = DesignPersistenceService(db).save_professional_design(
        organization_id=org,
        project_id=project,
        result={
            "project_name": "Clinic Project",
            "design_version": "v4",
            "design_quality_score": 91,
            "design_status": "PASS",
            "load": {"daily_energy_kwh": 10, "monthly_energy_kwh": 300, "connected_load_w": 2500, "diversity_adjusted_peak_w": 1800, "surge_peak_w": 3000},
            "pv": {"pv_capacity_kwp": 3.5, "required_kwp": 3.2},
            "battery": {"nominal_battery_kwh": 20, "system_voltage_v": 48, "battery_capacity_ah": 417, "autonomy_days": 2},
            "inverter": {"recommended_continuous_w": 3000, "recommended_surge_w": 5000},
            "electrical": {},
            "validation": {"warnings": [], "errors": []},
            "assumptions_register": [],
        },
    )
    report = ProfessionalReportService(db).generate_for_design(organization_id=org, design_id=saved["design_id"])
    assert report["report_id"]
    assert report["pdf_bytes"].startswith(b"%PDF")
    rows = repo.list_records("reports", "design_id=?", (saved["design_id"],))
    assert len(rows) == 1
    assert rows[0]["file_path"]


def test_report_rejects_other_organization(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    u1 = repo.create_user("a@example.com")
    u2 = repo.create_user("b@example.com")
    o1 = repo.create_organization("A", u1)
    o2 = repo.create_organization("B", u2)
    p = repo.create_project(o1, "Project")
    saved = DesignPersistenceService(db).save_professional_design(organization_id=o1, project_id=p, result={"design_quality_score": 80})
    try:
        ProfessionalReportService(db).generate_for_design(organization_id=o2, design_id=saved["design_id"])
    except ValueError:
        return
    assert False, "Expected organization ownership validation"
