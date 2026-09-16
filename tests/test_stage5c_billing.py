import json
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.billing_service import BillingService
from app.services.subscription_service import SubscriptionService, UsageLimitError
from app.billing.payment_provider import PlaceholderPaymentProvider


def make_org(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    uid = repo.create_user("billing@example.com", "Billing User")
    oid = repo.create_organization("Billing Org", uid)
    repo.add_member(oid, uid, "owner")
    return db, oid


def test_stage5c_schema_and_placeholder_checkout(tmp_path):
    db, oid = make_org(tmp_path)
    assert db.schema_version() == 6
    assert "billing_events" in db.table_names()
    assert "billing_checkout_sessions" in db.table_names()
    billing = BillingService(db, PlaceholderPaymentProvider())
    result = billing.create_upgrade_checkout(oid, "professional")
    assert result.success
    assert result.checkout.status == "pending"
    repo = PlatformRepository(db)
    sessions = repo.list_records("billing_checkout_sessions")
    assert len(sessions) == 1
    assert sessions[0]["plan_code"] == "professional"


def test_stage5c_provider_event_is_idempotent(tmp_path):
    db, oid = make_org(tmp_path)
    billing = BillingService(db)
    assert billing.apply_provider_event("evt_1", oid, "subscription_activated", "professional") is True
    assert billing.subscriptions.current_plan(oid).code == "professional"
    assert billing.apply_provider_event("evt_1", oid, "subscription_activated", "professional") is False
    assert len(PlatformRepository(db).list_records("billing_events")) == 1


def test_stage5c_failed_payment_changes_status(tmp_path):
    db, oid = make_org(tmp_path)
    billing = BillingService(db)
    billing.subscriptions.set_plan(oid, "professional")
    assert billing.apply_provider_event("evt_fail", oid, "payment_failed") is True
    assert billing.subscriptions.subscription(oid)["status"] == "past_due"
