"""Replaceable payment-provider boundary for Stage 5C.

No real payment is processed here. A future Stripe/Paystack/Flutterwave
adapter can implement the same interface without changing subscription logic.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import uuid

@dataclass(frozen=True)
class CheckoutSession:
    id: str
    organization_id: str
    plan_code: str
    status: str
    checkout_url: str | None = None

class PaymentProvider(Protocol):
    def create_checkout_session(self, organization_id: str, plan_code: str) -> CheckoutSession: ...
    def cancel_subscription(self, provider_subscription_id: str) -> bool: ...

class PlaceholderPaymentProvider:
    """Safe development provider: creates no charge and no external payment."""
    def create_checkout_session(self, organization_id: str, plan_code: str) -> CheckoutSession:
        return CheckoutSession(
            id=f"checkout_{uuid.uuid4().hex}",
            organization_id=organization_id,
            plan_code=plan_code,
            status="pending",
            checkout_url=None,
        )

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return True
