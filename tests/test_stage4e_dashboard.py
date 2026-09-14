from __future__ import annotations

import sqlite3

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.dashboard_service import latest_quality, designs_for_projects


def test_dashboard_workspace_counts_and_quality(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user_id = repo.create_user("demo@example.com", "Demo User", "usr_demo")
    org_id = repo.create_organization("Demo Org", user_id, "org_demo")

    customer_id = repo.create_customer(org_id, "Demo Customer")
    project_id = repo.create_project(org_id, "Demo Project", customer_id)
    design_id = repo.create_design(project_id, "Engineering Design", "v4")
    repo.save_design_result(design_id, "engineering", {"status": "PASS"}, quality_score=92)

    customers = repo.list_records("customers", "organization_id=?", (org_id,))
    projects = repo.list_records("projects", "organization_id=?", (org_id,))
    designs = designs_for_projects(repo, projects)

    assert len(customers) == 1
    assert len(projects) == 1
    assert len(designs) == 1
    assert latest_quality(repo, design_id) == 92.0


def test_dashboard_does_not_create_duplicate_product_database(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    user_id = repo.create_user("demo2@example.com", "Demo User 2", "usr_demo2")
    repo.create_organization("Demo Org 2", user_id, "org_demo2")

    tables = set(db.table_names())
    assert "products" not in tables
    assert "users" in tables
    assert "projects" in tables
    assert "designs" in tables
