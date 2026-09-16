"""Streamlit UI for the Stage 4B customer and project workspace."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.project_service import ProjectService
from app.services.subscription_service import SubscriptionService, UsageLimitError

DEMO_USER_ID = "usr_local_workspace"
DEMO_EMAIL = "workspace@solar-pv-designer.local"
DEMO_ORG_ID = "org_local_workspace"
DEMO_ORG_NAME = "My Solar Design Workspace"


def _ensure_workspace(repo: PlatformRepository) -> str:
    """Return the authenticated organization; retain legacy fallback for tests."""
    org_id = st.session_state.get("current_organization_id")
    if org_id and repo.get_one("organizations", org_id):
        return org_id
    # Legacy Stage 4 fallback is intentionally retained for isolated tests.
    if not repo.get_one("users", DEMO_USER_ID):
        repo.create_user(DEMO_EMAIL, "Workspace User", DEMO_USER_ID)
    if not repo.get_one("organizations", DEMO_ORG_ID):
        repo.create_organization(DEMO_ORG_NAME, DEMO_USER_ID, DEMO_ORG_ID)
    return DEMO_ORG_ID


def _records(repo: PlatformRepository, table: str, where: str = "", params: tuple = ()) -> list[dict[str, Any]]:
    return repo.list_records(table, where=where, params=params)


def render_project_management_ui() -> None:
    """Render customers, projects and design workspace management."""
    db = PlatformDatabase()
    repo = PlatformRepository(db)
    service = ProjectService(db)
    subscription = SubscriptionService(db)
    org_id = _ensure_workspace(repo)

    st.title("👥 Customers & Projects")
    st.caption("Manage customers and solar projects in your professional workspace.")

    customers = _records(repo, "customers", "organization_id=?", (org_id,))
    sites = _records(repo, "sites", "organization_id=?", (org_id,))
    projects = _records(repo, "projects", "organization_id=?", (org_id,))
    designs = []
    for project in projects:
        designs.extend(_records(repo, "designs", "project_id=?", (project["id"],)))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customers", len(customers))
    c2.metric("Sites", len(sites))
    c3.metric("Projects", len(projects))
    c4.metric("Designs", len(designs))

    tab_customer, tab_site, tab_project, tab_design = st.tabs(["👤 Customers", "📍 Sites", "📁 Projects", "⚡ Designs"])

    with tab_customer:
        st.subheader("Customer Management")
        with st.form("create_customer_form", clear_on_submit=True):
            name = st.text_input("Customer name *")
            email = st.text_input("Email")
            customer_type = st.selectbox("Customer type", ["individual", "company", "government", "ngo", "other"])
            contact_person = st.text_input("Contact person")
            phone = st.text_input("Phone")
            address = st.text_input("Billing/contact address")
            notes = st.text_area("Customer notes")
            submitted = st.form_submit_button("➕ Add Customer", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Customer name is required.")
                else:
                    try:
                        subscription.require_limit(org_id, "customers")
                        repo.create_customer(org_id, name, email, phone, address, notes, customer_type, contact_person)
                        subscription.repository.record_usage(org_id, "customers", 1)
                        st.success("Customer created successfully.")
                        st.rerun()
                    except UsageLimitError as exc:
                        st.warning(str(exc))

        if customers:
            customer_rows = [{
                "Name": c["name"], "Email": c["email"], "Phone": c["phone"],
                "Type": c.get("customer_type", "individual"), "Contact": c.get("contact_person", ""),
                "Address": c["address"], "Created": c["created_at"],
            } for c in customers]
            st.dataframe(pd.DataFrame(customer_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No customers yet. Add your first customer above.")

    with tab_site:
        st.subheader("Site Management")
        st.caption("Store installation sites separately from customer records so one customer can have multiple solar sites.")
        customer_options = {"No customer": None, **{f'{c["name"]} ({c["id"][-6:]})': c["id"] for c in customers}}
        with st.form("create_site_form", clear_on_submit=True):
            site_name = st.text_input("Site name *")
            site_customer = st.selectbox("Customer", list(customer_options.keys()), key="site_customer")
            site_address = st.text_input("Site address")
            col1, col2 = st.columns(2)
            latitude = col1.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
            longitude = col2.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")
            site_notes = st.text_area("Site notes")
            submitted = st.form_submit_button("📍 Add Site", use_container_width=True)
            if submitted:
                if not site_name.strip():
                    st.error("Site name is required.")
                else:
                    try:
                        subscription.require_limit(org_id, "sites")
                        repo.create_site(org_id, site_name, customer_options[site_customer], site_address, latitude, longitude, site_notes)
                        subscription.repository.record_usage(org_id, "sites", 1)
                        st.success("Site created successfully.")
                        st.rerun()
                    except UsageLimitError as exc:
                        st.warning(str(exc))

        if sites:
            customer_map = {c["id"]: c["name"] for c in customers}
            site_rows = [{
                "Site": x["name"], "Customer": customer_map.get(x.get("customer_id"), "—"),
                "Address": x.get("address", ""), "Latitude": x.get("latitude", "—"),
                "Longitude": x.get("longitude", "—"), "Created": x.get("created_at", ""),
            } for x in sites]
            st.dataframe(pd.DataFrame(site_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No sites yet. Add an installation site above.")

    with tab_project:
        st.subheader("Project Management")
        customer_options = {"No customer": None, **{f'{c["name"]} ({c["id"][-6:]})': c["id"] for c in customers}}
        site_options = {"No site": None, **{f'{x["name"]} ({x["id"][-6:]})': x["id"] for x in sites}}
        with st.form("create_project_form", clear_on_submit=True):
            project_name = st.text_input("Project name *")
            customer_label = st.selectbox("Customer", list(customer_options.keys()), key="project_customer")
            site_label = st.selectbox("Installation site", list(site_options.keys()), key="project_site")
            location = st.text_input("Project location")
            status = st.selectbox("Status", ["draft", "active", "completed", "archived"])
            notes = st.text_area("Project notes")
            submitted = st.form_submit_button("➕ Create Project", use_container_width=True)
            if submitted:
                if not project_name.strip():
                    st.error("Project name is required.")
                else:
                    try:
                        subscription.require_limit(org_id, "projects")
                        project_id = repo.create_project(
                            org_id, project_name, customer_options[customer_label], location, notes, None, site_options[site_label]
                        )
                        if status != "draft":
                            repo.update_record("projects", project_id, {"status": status})
                        subscription.repository.record_usage(org_id, "projects", 1)
                        st.success(f"Project created: {project_name}")
                        st.rerun()
                    except UsageLimitError as exc:
                        st.warning(str(exc))

        if projects:
            project_rows = []
            customer_map = {c["id"]: c["name"] for c in customers}
            site_map = {x["id"]: x["name"] for x in sites}
            for p in projects:
                project_rows.append({
                    "Project": p["name"],
                    "Customer": customer_map.get(p["customer_id"], "—"),
                    "Site": site_map.get(p.get("site_id"), "—"),
                    "Status": p["status"],
                    "Location": p["location"],
                    "Created": p["created_at"],
                })
            st.dataframe(pd.DataFrame(project_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No projects yet. Create a project above.")

    with tab_design:
        st.subheader("Design Workspace")
        if not projects:
            st.info("Create a project first, then create engineering design versions here.")
        else:
            project_map = {f'{p["name"]} ({p["id"][-6:]})': p["id"] for p in projects}
            selected_project_label = st.selectbox("Project", list(project_map.keys()))
            selected_project_id = project_map[selected_project_label]
            selected_project = repo.get_one("projects", selected_project_id)
            project_designs = _records(repo, "designs", "project_id=?", (selected_project_id,))

            with st.form("create_design_form", clear_on_submit=True):
                design_name = st.text_input("Design name *", value="Professional Engineering Design")
                engine_version = st.selectbox("Engineering engine", ["v4", "v3", "v2"])
                submitted = st.form_submit_button("⚡ Create Design Version", use_container_width=True)
                if submitted:
                    if not design_name.strip():
                        st.error("Design name is required.")
                    else:
                        try:
                            subscription.require_limit(org_id, "design_versions_created")
                            design_id = service.create_design(selected_project_id, design_name, engine_version)
                            subscription.repository.record_usage(org_id, "design_versions_created", 1)
                            st.success(f"Design version created: {design_id[-12:]}")
                            st.rerun()
                        except UsageLimitError as exc:
                            st.warning(str(exc))

            if project_designs:
                rows = [{
                    "Design": d["name"], "Version": d["version"],
                    "Status": d["status"], "Engine": d["engine_version"],
                    "Created": d["created_at"],
                } for d in project_designs]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with st.expander("Project details", expanded=False):
                st.write(f"**Project:** {selected_project['name']}")
                st.write(f"**Site:** {site_map.get(selected_project.get('site_id'), 'Not specified')}")
                st.write(f"**Location:** {selected_project['location'] or 'Not specified'}")
                st.write(f"**Notes:** {selected_project['notes'] or 'None'}")
