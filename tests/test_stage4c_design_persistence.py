import json
from pathlib import Path
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.design_persistence_service import DesignPersistenceService

def test_save_design_result_and_equipment(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db"); repo = PlatformRepository(db)
    user = repo.create_user("test@example.com", "Test User")
    org = repo.create_organization("Test Solar", user)
    project = repo.create_project(org, "House Project")
    service = DesignPersistenceService(db)
    selection = {"selected": {"pv_module": {"product": {"id":"pv-1","name":"PV 550W"}, "validation": {"valid":True}}, "battery": {"product": {"id":"bat-1","name":"Battery"}, "validation": {"valid":True}}}}
    result = {"project_name":"House Project","design_version":"v4","design_quality_score":92.0,"pv":{"pv_capacity_kwp":5.5}}
    saved = service.save_professional_design(organization_id=org, project_id=project, result=result, equipment_selection=selection)
    assert saved["version"] == 1
    loaded = service.load_design_result(saved["design_id"])
    assert loaded and loaded["result"]["pv"]["pv_capacity_kwp"] == 5.5
    eq = repo.list_records("design_equipment", "design_id=?", (saved["design_id"],))
    assert len(eq) == 2
    usage = repo.list_records("usage_records", "organization_id=?", (org,))
    assert any(x["metric"] == "professional_designs_saved" for x in usage)

def test_design_versions_increment(tmp_path: Path):
    db=PlatformDatabase(tmp_path/"p.db"); repo=PlatformRepository(db)
    u=repo.create_user("a@b.com"); o=repo.create_organization("Org",u); p=repo.create_project(o,"P")
    service=DesignPersistenceService(db); r={"project_name":"P","design_quality_score":80}
    a=service.save_professional_design(organization_id=o, project_id=p, result=r)
    b=service.save_professional_design(organization_id=o, project_id=p, result=r)
    assert (a["version"], b["version"]) == (1,2)
