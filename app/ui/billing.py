"""Stage 5C billing UI: architecture-ready, payment-safe placeholder."""
import streamlit as st
from app.services.billing_service import BillingService
from app.services.subscription_service import PLANS

def render_billing_ui() -> None:
    org_id = st.session_state.get("current_organization_id")
    if not org_id:
        st.info("Sign in to manage billing.")
        return
    service = BillingService()
    current = service.subscriptions.current_plan(org_id)
    sub = service.subscriptions.subscription(org_id)
    st.title("💳 Billing & Subscription")
    st.caption("Stage 5C payment architecture. Live payment processing is not connected yet.")
    st.metric("Current plan", current.name)
    st.write(f"Subscription status: **{str(sub.get('status', 'active')).title()}**")

    st.subheader("Change plan")
    for code, plan in PLANS.items():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{plan.name}** — {plan.description}")
            if code == current.code:
                c2.success("Current")
            else:
                if c2.button("Request checkout", key=f"checkout_{code}"):
                    result = service.create_upgrade_checkout(org_id, code)
                    if result.success:
                        st.success(result.message)
                        st.info("When a real payment provider is connected, this action will redirect the customer to the provider checkout page. No money is charged in Stage 5C.")
                    else:
                        st.warning(result.message)

    st.divider()
    st.subheader("Payment integration status")
    st.info("Provider adapter: PlaceholderPaymentProvider • Webhook boundary: ready • Live keys: not configured • Automatic charging: disabled")
