from pathlib import Path

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.subscription_service import SubscriptionService


def _repo(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user = repo.create_user("owner@example.com", "Owner")
    org = repo.create_organization("Solar Company", user)
    return db, repo, org


def test_stage6a_schema_and_site_workspace(tmp_path: Path):
    db, repo, org = _repo(tmp_path)
    assert db.schema_version() == 7
    tables = set(db.table_names())
    assert "sites" in tables
    customer = repo.create_customer(org, "Acme Energy", customer_type="company", contact_person="Amina")
    site = repo.create_site(org, "Acme Main Site", customer, "Kampala", 0.3476, 32.5825)
    project = repo.create_project(org, "Acme Solar", customer, "Kampala", "Rooftop PV", site_id=site)
    saved_customer = repo.get_one("customers", customer)
    saved_site = repo.get_one("sites", site)
    saved_project = repo.get_one("projects", project)
    assert saved_customer["customer_type"] == "company"
    assert saved_customer["contact_person"] == "Amina"
    assert saved_site["customer_id"] == customer
    assert saved_project["site_id"] == site


def test_stage6a_site_limit_exists_for_all_plans(tmp_path: Path):
    db, repo, org = _repo(tmp_path)
    service = SubscriptionService(db)
    assert service.plans()["free"].limit_for("sites") == 10
    assert service.plans()["professional"].limit_for("sites") == 250
    assert service.plans()["business"].limit_for("sites") is None
