"""Streamlit UI for sandbox email delivery and delivery-log inspection."""
from __future__ import annotations
import streamlit as st
from app.services.email_service import EmailMessage, EmailService

def render_email_delivery_ui():
    st.header("✉️ Email Delivery")
    st.caption("Sandbox mode: messages are recorded for testing; no external email is sent.")
    org_id = st.session_state.get("current_organization_id")
    if not org_id:
        st.warning("Select an organization first.")
        return
    with st.form("email_delivery_test"):
        recipient = st.text_input("Recipient email")
        subject = st.text_input("Subject", value="Solar PV proposal notification")
        body = st.text_area("Message", value="Your proposal is available for review.")
        submitted = st.form_submit_button("Send sandbox email")
    if submitted:
        try:
            result = EmailService().send(org_id, EmailMessage(recipient, subject, body), "manual_test")
            st.success(f"Email recorded: {result['id']}")
        except ValueError as exc:
            st.error(str(exc))
