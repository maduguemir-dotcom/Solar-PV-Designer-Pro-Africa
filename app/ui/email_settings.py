"""UI for documenting production email configuration without exposing secrets."""
from __future__ import annotations
import streamlit as st

def render_email_settings_ui():
    st.header("⚙️ Email Provider Settings")
    st.info("Production credentials should be configured through deployment secrets, not committed to GitHub.")
    st.markdown("**Supported architecture:** Sandbox and SMTP adapters; additional providers can be added without changing notification templates.")
    st.code("EMAIL_PROVIDER=smtp\nEMAIL_SMTP_HOST=smtp.example.com\nEMAIL_SMTP_PORT=587\nEMAIL_SMTP_USERNAME=...\nEMAIL_SMTP_PASSWORD=...\nEMAIL_SENDER=notifications@example.com\nEMAIL_SMTP_USE_TLS=true", language="bash")
    st.warning("The settings shown are configuration guidance only. This screen does not store or transmit credentials.")
