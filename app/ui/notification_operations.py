def render_notification_operations(service, organization_id, *, actor=None, secure_service=None):
    """Render notification operations with authorization-aware recovery controls.

    ``service`` remains the metrics provider. Recovery buttons use ``secure_service``
    when supplied; this is the production path introduced in Stage 6S.

    actor must be a mapping containing role, user_id and organization_id when
    secure_service is supplied. The UI intentionally does not accept a role
    from a Streamlit widget; it must come from the authenticated session.
    """
    import streamlit as st

    metrics = service.metrics(organization_id)
    st.subheader("Notification Operations")
    cols = st.columns(5)
    for col, key in zip(cols, ("queued", "processing", "sent", "failed", "dead_letter")):
        col.metric(key.replace("_", " ").title(), metrics[key])
    st.metric("Attention required", metrics["attention_required"])

    if secure_service is None:
        st.info("Administrative recovery controls are unavailable until secure operations are configured.")
        return

    if not actor:
        st.warning("Administrative identity is required for notification recovery operations.")
        return

    required = {"role", "user_id", "organization_id"}
    if not required.issubset(actor):
        st.error("Administrative identity is incomplete; recovery controls are disabled.")
        return

    if actor["organization_id"] != organization_id:
        st.error("The current administrator is not scoped to this organization.")
        return

    if st.button("Retry eligible failed notifications"):
        count = secure_service.retry_failed(
            role=actor["role"],
            organization_id=organization_id,
            actor_organization_id=actor["organization_id"],
            actor_user_id=actor["user_id"],
        )
        st.success(f"Requeued {count} notification(s).")

    if st.button("Requeue dead-letter notifications"):
        count = secure_service.requeue_dead_letter(
            role=actor["role"],
            organization_id=organization_id,
            actor_organization_id=actor["organization_id"],
            actor_user_id=actor["user_id"],
        )
        st.warning(f"Requeued {count} notification(s).")
