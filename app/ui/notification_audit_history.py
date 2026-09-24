"""Streamlit presentation for organization-scoped notification audit history."""


def render_notification_audit_history(history_service, organization_id):
    import streamlit as st

    st.subheader("Notification Audit History")
    col1, col2, col3 = st.columns(3)
    with col1:
        outcome = st.selectbox("Outcome", ["All", "allowed", "denied"])
    with col2:
        action = st.selectbox(
            "Action",
            ["All", "retry_failed", "requeue_dead_letter"],
        )
    with col3:
        limit = st.number_input("Rows", min_value=1, max_value=500, value=100, step=10)

    events = history_service.list_history(
        organization_id,
        outcome=None if outcome == "All" else outcome,
        action=None if action == "All" else action,
        limit=int(limit),
    )

    if not events:
        st.info("No notification audit events match the selected filters.")
        return

    rows = []
    for event in events:
        rows.append({
            "Time": event.get("created_at", ""),
            "Actor": event.get("actor_user_id", ""),
            "Action": event.get("action", ""),
            "Target": event.get("target", ""),
            "Outcome": event.get("outcome", ""),
            "Details": event.get("details_json", event.get("details", "")),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
