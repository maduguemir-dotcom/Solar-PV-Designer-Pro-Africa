"""Deterministic sandbox payment provider for end-to-end billing tests.

This provider never charges real money. It creates signed webhook payloads so
Stage 5D can exercise the same verification/idempotency boundary used in
production adapters.
"""
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass
from .payment_provider import CheckoutSession
from .webhook_security import sign_payload

@dataclass(frozen=True)
class SandboxEvent:
    event_id: str
    event_type: str
    payload: bytes
    signature: str

class SandboxPaymentProvider:
    provider_name = "sandbox"

    def __init__(self, webhook_secret: str = "stage5d-sandbox-secret"):
        self.webhook_secret = webhook_secret

    def create_checkout_session(self, organization_id: str, plan_code: str) -> CheckoutSession:
        sid = f"sandbox_chk_{uuid.uuid4().hex}"
        return CheckoutSession(sid, organization_id, plan_code, "pending", f"https://sandbox.invalid/checkout/{sid}")

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return bool(provider_subscription_id)

    def event(self, event_type: str, organization_id: str, plan_code: str | None = None,
              provider_subscription_id: str | None = None) -> SandboxEvent:
        body = {
            "event_id": f"sandbox_evt_{uuid.uuid4().hex}",
            "event_type": event_type,
            "organization_id": organization_id,
            "plan_code": plan_code,
            "provider_subscription_id": provider_subscription_id,
        }
        payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return SandboxEvent(body["event_id"], event_type, payload, sign_payload(payload, self.webhook_secret))
