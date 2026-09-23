def render_notification_operations(service, organization_id):
    """Render an administrative queue-monitoring page; imports Streamlit lazily."""
    import streamlit as st
    metrics = service.metrics(organization_id)
    st.subheader("Notification Operations")
    cols = st.columns(5)
    for col, key in zip(cols, ("queued", "processing", "sent", "failed", "dead_letter")):
        col.metric(key.replace("_", " ").title(), metrics[key])
    st.metric("Attention required", metrics["attention_required"])
    if st.button("Retry eligible failed notifications"):
        st.success(f"Requeued {service.retry_failed(organization_id)} notification(s).")
    if st.button("Requeue dead-letter notifications"):
        st.warning(f"Requeued {service.requeue_dead_letter(organization_id)} notification(s).")
