import json
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.billing_service import BillingService
from app.billing.sandbox_provider import SandboxPaymentProvider
from app.billing.webhook_security import sign_payload, verify_signature


def make_org(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    repo = PlatformRepository(db)
    uid = repo.create_user("stage5d@example.com", "Stage 5D User")
    oid = repo.create_organization("Stage 5D Org", uid)
    return db, oid


def test_signature_verification_and_tamper_detection():
    payload = b'{"event":"subscription_activated"}'
    sig = sign_payload(payload, "secret")
    assert verify_signature(payload, sig, "secret")
    assert not verify_signature(payload + b"x", sig, "secret")
    assert not verify_signature(payload, sig, "wrong")


def test_verified_sandbox_webhook_activates_subscription(tmp_path):
    db, oid = make_org(tmp_path)
    provider = SandboxPaymentProvider("secret")
    billing = BillingService(db, provider)
    event = provider.event("subscription_activated", oid, "professional", "sub_sandbox_1")
    assert billing.process_verified_webhook(event.payload, event.signature, provider.webhook_secret)
    assert billing.subscriptions.current_plan(oid).code == "professional"
    sub = billing.subscriptions.subscription(oid)
    assert sub["provider_subscription_id"] == "sub_sandbox_1"


def test_webhook_replay_is_idempotent(tmp_path):
    db, oid = make_org(tmp_path)
    provider = SandboxPaymentProvider("secret")
    billing = BillingService(db, provider)
    event = provider.event("subscription_activated", oid, "professional", "sub_1")
    assert billing.process_verified_webhook(event.payload, event.signature, provider.webhook_secret)
    assert not billing.process_verified_webhook(event.payload, event.signature, provider.webhook_secret)
    assert len(PlatformRepository(db).list_records("billing_events")) == 1


def test_invalid_webhook_is_rejected(tmp_path):
    db, oid = make_org(tmp_path)
    provider = SandboxPaymentProvider("secret")
    billing = BillingService(db, provider)
    event = provider.event("subscription_activated", oid, "professional", "sub_1")
    try:
        billing.process_verified_webhook(event.payload, "bad", provider.webhook_secret)
    except ValueError as exc:
        assert "signature" in str(exc).lower()
    else:
        raise AssertionError("Invalid signature should be rejected")
