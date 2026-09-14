from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.subscription_service import SubscriptionService, UsageLimitError, PLANS


def make_service(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    uid = repo.create_user("owner@example.com", "Owner")
    org = repo.create_organization("Test Solar", uid)
    return db, repo, SubscriptionService(db), org


def test_new_org_defaults_to_free(tmp_path):
    db, repo, service, org = make_service(tmp_path)
    assert service.current_plan(org).code == "free"
    assert service.remaining(org, "projects") == 3


def test_usage_limit_enforced(tmp_path):
    db, repo, service, org = make_service(tmp_path)
    for _ in range(3):
        service.record_if_allowed(org, "projects")
    assert service.usage_this_month(org, "projects") == 3
    with pytest.raises(UsageLimitError):
        service.record_if_allowed(org, "projects")


def test_unlimited_business_metric(tmp_path):
    db, repo, service, org = make_service(tmp_path)
    service.set_plan(org, "business")
    assert service.remaining(org, "projects") is None
    for _ in range(20):
        service.record_if_allowed(org, "projects")
    assert service.usage_this_month(org, "projects") == 20


def test_feature_flags(tmp_path):
    db, repo, service, org = make_service(tmp_path)
    assert not service.feature_enabled(org, "advanced_design")
    service.set_plan(org, "professional")
    assert service.feature_enabled(org, "advanced_design")
    assert service.feature_enabled(org, "ai_assistance")


def test_all_plans_have_core_entitlements():
    assert set(PLANS) == {"free", "professional", "business"}
    for plan in PLANS.values():
        assert "projects" in plan.limits
        assert "professional_designs_saved" in plan.limits
