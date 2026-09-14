"""Streamlit authentication and organization context UI for Stage 5A."""
from __future__ import annotations
import streamlit as st
from app.auth.service import AuthService
from app.platform.database import PlatformDatabase


def _service() -> AuthService:
    return AuthService(PlatformDatabase())


def current_identity() -> dict | None:
    return st.session_state.get("authenticated_user")


def current_organization_id() -> str | None:
    return st.session_state.get("current_organization_id")


def render_auth_gate() -> bool:
    """Return True when an authenticated user may enter the application."""
    if current_identity():
        return True
    auth = _service()
    st.title("☀️ Solar PV Designer Pro Africa™")
    st.subheader("Professional Workspace Access")
    st.caption("Stage 5A authentication foundation — create an account or sign in to continue.")
    login, register = st.tabs(["🔐 Sign In", "🆕 Create Account"])
    with login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                identity = auth.authenticate(email, password)
                if identity:
                    st.session_state.authenticated_user = identity
                    st.session_state.current_organization_id = identity["organization_id"]
                    st.rerun()
                else:
                    st.error("Invalid email/password or inactive account.")
    with register:
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            email = st.text_input("Email", key="register_email")
            organization = st.text_input("Organization / Company name")
            password = st.text_input("Password", type="password", key="register_password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        result = auth.register(email, password, full_name, organization)
                        identity = auth.authenticate(email, password)
                        if identity:
                            st.session_state.authenticated_user = identity
                            st.session_state.current_organization_id = result["organization_id"]
                            st.success("Account created successfully.")
                            st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                    except Exception as exc:
                        if "UNIQUE constraint failed: users.email" in str(exc):
                            st.error("An account with this email already exists. Please sign in.")
                        else:
                            st.error("Unable to create the account.")
                            st.exception(exc)
    st.stop()


def render_authenticated_sidebar() -> None:
    identity = current_identity()
    if not identity:
        return
    st.sidebar.success(f"Signed in as {identity['full_name'] or identity['email']}")
    auth = _service()
    orgs = auth.repository.organizations_for_user(identity["user_id"])
    if orgs:
        labels = {f"{o['name']} ({o['member_role']})": o["id"] for o in orgs}
        current = current_organization_id()
        current_label = next((label for label, oid in labels.items() if oid == current), next(iter(labels)))
        selected = st.sidebar.selectbox("Organization", list(labels), index=list(labels).index(current_label))
        if labels[selected] != current:
            st.session_state.current_organization_id = labels[selected]
            st.rerun()
    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state.pop("authenticated_user", None)
        st.session_state.pop("current_organization_id", None)
        st.rerun()
