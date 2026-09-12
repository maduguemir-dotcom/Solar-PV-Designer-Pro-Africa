"""Stage 4B tests for customer/project/design management."""
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.project_service import ProjectService


def test_customer_project_design_workflow(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user_id = repo.create_user("user@example.com", "Test User")
    org_id = repo.create_organization("Test Solar Company", user_id)

    customer_id = repo.create_customer(org_id, "Amina Customer", "amina@example.com")
    project_id = repo.create_project(org_id, "Amina Solar Home", customer_id, "Kampala")

    service = ProjectService(db)
    design1 = service.create_design(project_id, "Initial Design")
    design2 = service.create_design(project_id, "Revised Design")

    assert repo.get_one("customers", customer_id)["name"] == "Amina Customer"
    assert repo.get_one("projects", project_id)["customer_id"] == customer_id
    assert repo.get_one("designs", design1)["version"] == 1
    assert repo.get_one("designs", design2)["version"] == 2


def test_project_listing_is_organization_scoped(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    u1 = repo.create_user("one@example.com")
    u2 = repo.create_user("two@example.com")
    o1 = repo.create_organization("Org One", u1)
    o2 = repo.create_organization("Org Two", u2)
    repo.create_project(o1, "Project One")
    repo.create_project(o2, "Project Two")

    rows = repo.list_records("projects", "organization_id=?", (o1,))
    assert len(rows) == 1
    assert rows[0]["name"] == "Project One"


def test_project_status_update(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user_id = repo.create_user("status@example.com")
    org_id = repo.create_organization("Status Org", user_id)
    project_id = repo.create_project(org_id, "Status Project")

    repo.update_record("projects", project_id, {"status": "active"})
    assert repo.get_one("projects", project_id)["status"] == "active"
