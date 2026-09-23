from __future__ import annotations
import streamlit as st
from services.notification_preferences_service import NotificationPreferencesService

def render_notification_preferences_ui(database, organization_id):
    st.header("🔔 Notification Preferences")
    service = NotificationPreferencesService(database)
    current = service.get(organization_id)
    with st.form("notification_preferences_form"):
        values = {k: st.checkbox(k.replace('_',' ').title(), value=v) for k,v in current.items()}
        if st.form_submit_button("Save Notification Preferences"):
            service.save(organization_id, values); st.success("Notification preferences saved.")
