"""Administrator-facing notification operations health dashboard."""


def render_notification_health_dashboard(
    health_service,
    organization_id,
    *,
    audit_history_renderer=None,
    reliability_renderer=None,
    recovery_renderer=None,
):
    import streamlit as st

    st.subheader("Notification Operations Health")
    limit = st.number_input(
        "Audit events analyzed",
        min_value=1,
        max_value=5000,
        value=500,
        step=100,
        key="notification_health_limit",
    )
    snapshot = health_service.snapshot(organization_id, limit=int(limit))
    summary = snapshot["summary"]

    cols = st.columns(4)
    cols[0].metric("Audit Events", summary["total_events"])
    cols[1].metric("Allowed", summary["allowed_events"])
    cols[2].metric("Denied", summary["denied_events"])
    cols[3].metric("Denial Rate", f'{summary["denial_rate"]:.1f}%')

    cols2 = st.columns(3)
    cols2[0].metric("Retry Actions", summary["retry_failed_events"])
    cols2[1].metric("Dead-Letter Requeues", summary["requeue_dead_letter_events"])
    cols2[2].metric("Authorization Success", f'{summary["authorization_success_rate"]:.1f}%')

    latest = snapshot["latest_event"]
    if latest:
        st.caption(
            "Latest audit event: "
            f'{latest.get("created_at", "unknown")} — '
            f'{latest.get("action", "unknown")} — '
            f'{latest.get("outcome", "unknown")}'
        )
    else:
        st.info("No notification audit events are available for this organization.")

    if reliability_renderer:
        with st.expander("Reliability Metrics", expanded=True):
            reliability_renderer(organization_id, int(limit))

    if audit_history_renderer:
        with st.expander("Audit & Operations History", expanded=False):
            audit_history_renderer(organization_id, int(limit))

    if recovery_renderer:
        with st.expander("Recovery Operations", expanded=False):
            recovery_renderer(organization_id)
