"""Billing UI for subscription management and safe sandbox testing."""
import os
import streamlit as st
from app.services.billing_service import BillingService
from app.services.subscription_service import PLANS
from app.billing.sandbox_provider import SandboxPaymentProvider

def render_billing_ui() -> None:
    org_id = st.session_state.get("current_organization_id")
    if not org_id:
        st.info("Sign in to manage billing.")
        return
    service = BillingService()
    current = service.subscriptions.current_plan(org_id)
    sub = service.subscriptions.subscription(org_id)
    st.title("💳 Billing & Subscription")
    st.caption("Subscription management with a secure provider boundary. Live payment credentials are not stored in the application source.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current plan", current.name)
    c2.metric("Status", str(sub.get("status", "active")).replace("_", " ").title())
    c3.metric("Provider", "Not connected" if not sub.get("provider_subscription_id") else "Connected")

    st.subheader("Available plans")
    for code, plan in PLANS.items():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{plan.name}** — {plan.description}")
            if code == current.code:
                c2.success("Current")
            elif c2.button("Start checkout", key=f"checkout_{code}"):
                result = service.create_upgrade_checkout(org_id, code)
                if result.success:
                    st.success(result.message)
                    if result.checkout and result.checkout.checkout_url:
                        st.link_button("Open sandbox checkout", result.checkout.checkout_url)
                    else:
                        st.info("A provider checkout URL will appear here when a live payment adapter is configured.")
                else:
                    st.warning(result.message)

    st.divider()
    st.subheader("Payment integration status")
    live_secret_configured = bool(os.getenv("SOLAR_PV_PAYMENT_WEBHOOK_SECRET"))
    st.info(
        "Production payment adapters are intentionally not enabled yet. "
        f"Webhook secret configured: {'Yes' if live_secret_configured else 'No'}"
    )
    st.caption("Never commit payment API keys or webhook secrets. Supply them through the deployment environment/secrets manager.")

    with st.expander("Sandbox verification (developer/test mode)"):
        st.write("The sandbox provider creates no real charge. It is used to verify signed webhook processing and subscription reconciliation before connecting a live provider.")
        if st.button("Simulate successful Professional payment", key="sandbox_professional"):
            provider = SandboxPaymentProvider()
            sandbox_service = BillingService(service.database, provider)
            event = provider.event("subscription_activated", org_id, "professional", "sandbox_sub_demo")
            sandbox_service.process_verified_webhook(event.payload, event.signature, provider.webhook_secret)
            st.success("Sandbox payment event verified and Professional subscription activated.")
            st.rerun()
