"""Drop-in administration workspace for notification operations.

The host application's admin navigation can call ``render_notification_admin_workspace``
from its existing administration page. Dependencies are injected so this module
remains independent of the application's routing and database wiring.
"""


def render_notification_admin_workspace(
    *,
    organization_id,
    health_renderer,
    reliability_renderer=None,
    audit_history_renderer=None,
    recovery_renderer=None,
    health_service=None,
):
    if not organization_id:
        raise ValueError("organization_id is required")
    if not callable(health_renderer):
        raise TypeError("health_renderer must be callable")

    import streamlit as st

    st.header("Notification Operations")
    st.caption("Organization-scoped administration, reliability, audit, and recovery controls.")

    tab_health, tab_history, tab_reliability, tab_recovery = st.tabs(
        ["Health", "Audit History", "Reliability", "Recovery"]
    )

    with tab_health:
        health_renderer(health_service, organization_id,
                        audit_history_renderer=audit_history_renderer,
                        reliability_renderer=reliability_renderer,
                        recovery_renderer=recovery_renderer)

    with tab_history:
        if audit_history_renderer:
            audit_history_renderer(organization_id)
        else:
            st.info("Audit history renderer is not configured.")

    with tab_reliability:
        if reliability_renderer:
            reliability_renderer(organization_id)
        else:
            st.info("Reliability renderer is not configured.")

    with tab_recovery:
        if recovery_renderer:
            recovery_renderer(organization_id)
        else:
            st.info("Recovery operations renderer is not configured.")
