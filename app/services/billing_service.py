"""Billing orchestration with verified, idempotent provider webhooks."""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional
from app.billing.payment_provider import CheckoutSession, PlaceholderPaymentProvider, PaymentProvider
from app.billing.webhook_security import verify_signature
from app.services.subscription_service import PLANS, SubscriptionService
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository

@dataclass(frozen=True)
class BillingResult:
    success: bool
    message: str
    checkout: Optional[CheckoutSession] = None

class BillingService:
    def __init__(self, database: Optional[PlatformDatabase] = None, provider: Optional[PaymentProvider] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)
        self.subscriptions = SubscriptionService(self.database)
        self.provider = provider or PlaceholderPaymentProvider()

    def create_upgrade_checkout(self, organization_id: str, plan_code: str) -> BillingResult:
        if plan_code not in PLANS:
            return BillingResult(False, "Unknown subscription plan.")
        current = self.subscriptions.current_plan(organization_id).code
        if plan_code == current:
            return BillingResult(False, "Your organization is already on this plan.")
        checkout = self.provider.create_checkout_session(organization_id, plan_code)
        self.repository.create_checkout_session(
            organization_id, plan_code, provider=getattr(self.provider, "provider_name", "placeholder"),
            provider_session_id=checkout.id
        )
        self.repository.create_billing_event(
            organization_id, "checkout_created", checkout.id,
            {"plan_code": plan_code, "status": checkout.status}
        )
        return BillingResult(True, "Checkout session created. No live charge is performed by the development provider.", checkout)

    def process_verified_webhook(self, payload: bytes, signature: str, webhook_secret: str) -> bool:
        if not verify_signature(payload, signature, webhook_secret):
            raise ValueError("Invalid webhook signature")
        try:
            event = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid webhook payload") from exc
        required = {"event_id", "event_type", "organization_id"}
        if not required.issubset(event):
            raise ValueError("Webhook payload is missing required fields")
        return self.apply_provider_event(
            event["event_id"], event["organization_id"], event["event_type"],
            event.get("plan_code"), event.get("provider_subscription_id"),
            provider_session_id=event.get("provider_session_id"),
            current_period_end=event.get("current_period_end"),
        )

    def apply_provider_event(self, event_id: str, organization_id: str, event_type: str,
                             plan_code: Optional[str] = None, provider_subscription_id: Optional[str] = None,
                             provider_session_id: Optional[str] = None, current_period_end: Optional[str] = None) -> bool:
        """Apply a verified provider event exactly once."""
        if self.repository.billing_event_exists(event_id):
            return False
        if event_type in {"subscription_activated", "subscription_updated"}:
            if plan_code not in PLANS:
                raise ValueError("Provider event contains an unknown plan")
            self.subscriptions.set_plan(organization_id, plan_code, "active")
            self.repository.update_subscription_for_org(
                organization_id, plan_code, "active", provider_subscription_id, current_period_end
            )
            if provider_session_id:
                self.repository.update_checkout_status(organization_id, provider_session_id, "completed")
        elif event_type == "subscription_cancelled":
            sub = self.subscriptions.subscription(organization_id)
            self.repository.update_subscription_for_org(
                organization_id, sub.get("plan_code", "free"), "cancelled", provider_subscription_id, current_period_end
            )
        elif event_type == "payment_failed":
            sub = self.subscriptions.subscription(organization_id)
            self.repository.update_subscription_for_org(
                organization_id, sub.get("plan_code", "free"), "past_due", provider_subscription_id, current_period_end
            )
        else:
            raise ValueError(f"Unsupported billing event: {event_type}")
        self.repository.create_billing_event(
            organization_id, event_type, event_id,
            {"plan_code": plan_code, "provider_subscription_id": provider_subscription_id,
             "provider_session_id": provider_session_id, "current_period_end": current_period_end}
        )
        return True
