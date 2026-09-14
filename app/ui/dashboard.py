"""Stage 4E professional dashboard and project history UI."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.ui.project_management import _ensure_workspace
from app.services.dashboard_service import safe_records, designs_for_projects, latest_quality



def render_dashboard_ui() -> None:
    """Render the professional organization dashboard."""
    db = PlatformDatabase()
    repo = PlatformRepository(db)
    org_id = _ensure_workspace(repo)

    customers = safe_records(repo, "customers", "organization_id=?", (org_id,))
    projects = safe_records(repo, "projects", "organization_id=?", (org_id,))
    designs = designs_for_projects(repo, projects)
    design_ids = tuple(d["id"] for d in designs)

    reports: list[dict[str, Any]] = []
    if design_ids:
        placeholders = ",".join("?" for _ in design_ids)
        reports = safe_records(repo, "reports", f"design_id IN ({placeholders})", design_ids)

    st.title("🏠 Professional Dashboard")
    st.caption("Your Solar PV Designer Pro Africa™ engineering and business workspace.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customers", len(customers))
    c2.metric("Projects", len(projects))
    c3.metric("Saved Designs", len(designs))
    c4.metric("Reports", len(reports))

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("📁 Recent Projects")
        if projects:
            customer_map = {c["id"]: c["name"] for c in customers}
            rows = [{
                "Project": p.get("name", ""),
                "Customer": customer_map.get(p.get("customer_id"), "—"),
                "Status": p.get("status", "draft"),
                "Location": p.get("location", "") or "—",
            } for p in projects[:8]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No projects yet. Open **Customers & Projects** to create your first project.")

    with right:
        st.subheader("⚡ Recent Designs")
        if designs:
            project_map = {p["id"]: p["name"] for p in projects}
            rows = []
            for d in designs[:8]:
                score = latest_quality(repo, d["id"])
                rows.append({
                    "Design": d.get("name", ""),
                    "Version": f'v{d.get("version", 1)}',
                    "Project": project_map.get(d.get("project_id"), "—"),
                    "Status": d.get("status", "draft"),
                    "Quality": f"{score:.0f}/100" if score is not None else "—",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No saved designs yet. Run a professional design and save it to a project.")

    st.subheader("📄 Recent Reports")
    if reports:
        design_map = {d["id"]: d for d in designs}
        rows = [{
            "Report": r.get("report_type", "engineering").title(),
            "Design": design_map.get(r.get("design_id"), {}).get("name", "—"),
            "Status": r.get("status", "generated"),
            "Created": r.get("created_at", ""),
        } for r in reports[:8]]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No professional reports have been generated yet.")

    st.subheader("🕘 Workspace Activity")
    activity = _organization_activity(repo, org_id)
    if activity:
        columns = ["Date", "Type", "Item", "Status"]
        st.dataframe(pd.DataFrame(activity[:12])[columns], use_container_width=True, hide_index=True)
    else:
        st.info("Workspace activity will appear here as you add customers, projects and designs.")
