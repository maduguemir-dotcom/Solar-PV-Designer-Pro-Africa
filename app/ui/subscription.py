"""Stage 5B Plans & Usage UI."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from app.platform.database import PlatformDatabase
from app.services.subscription_service import SubscriptionService


def render_subscription_ui() -> None:
    org_id = st.session_state.get("current_organization_id")
    if not org_id:
        st.info("Sign in to view your subscription and usage.")
        return
    service = SubscriptionService(PlatformDatabase())
    plan = service.current_plan(org_id)
    sub = service.subscription(org_id)

    st.title("💳 Plans & Usage")
    st.caption("Stage 5B commercial controls. Payment processing is not yet connected.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current plan", plan.name)
    c2.metric("Subscription", str(sub.get("status", "active")).title())
    c3.metric("Billing", "Not connected")

    st.subheader("Current monthly usage")
    rows = service.usage_summary(org_id)
    display = []
    for row in rows:
        display.append({
            "Resource": row["label"],
            "Used": row["used"],
            "Limit": "Unlimited" if row["limit"] is None else row["limit"],
            "Remaining": "Unlimited" if row["remaining"] is None else row["remaining"],
        })
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)

    st.subheader("Available plans")
    cols = st.columns(3)
    for col, candidate in zip(cols, service.plans().values()):
        with col:
            st.markdown(f"### {candidate.name}")
            st.write(candidate.description)
            for metric, limit in candidate.limits.items():
                label = metric.replace("_", " ").title()
                value = "Unlimited" if limit is None else str(limit)
                st.caption(f"{label}: {value}")
            if candidate.code == plan.code:
                st.success("Current plan")
            else:
                st.button("Upgrade / Change plan", key=f"plan_{candidate.code}", disabled=True)
    st.info("Plan changes are intentionally shown as a commercial placeholder in Stage 5B. Payment and billing integration will be implemented in Stage 5C.")
