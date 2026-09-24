"""Streamlit presentation for audit-derived notification reliability metrics."""


def render_notification_reliability(reliability_service, organization_id):
    import streamlit as st

    st.subheader("Notification Reliability")
    limit = st.number_input("Audit events analyzed", min_value=1, max_value=5000, value=500, step=100)
    summary = reliability_service.summarize(organization_id, limit=int(limit))

    cols = st.columns(4)
    cols[0].metric("Audit Events", summary["total_events"])
    cols[1].metric("Allowed", summary["allowed_events"])
    cols[2].metric("Denied", summary["denied_events"])
    cols[3].metric("Denial Rate", f'{summary["denial_rate"]:.1f}%')

    action_cols = st.columns(2)
    action_cols[0].metric("Retry Actions", summary["retry_failed_events"])
    action_cols[1].metric("Dead-Letter Requeues", summary["requeue_dead_letter_events"])

    trend = reliability_service.daily_trend(organization_id, limit=int(limit))
    if trend:
        st.caption("Audit-derived daily authorization/recovery activity")
        st.dataframe(trend, use_container_width=True, hide_index=True)
    else:
        st.info("No notification audit events are available for this organization.")
