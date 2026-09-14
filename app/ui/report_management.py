"""Stage 4D UI for generating reports from saved designs."""
from __future__ import annotations
import streamlit as st
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.professional_report_service import ProfessionalReportService
from app.ui.project_management import _ensure_workspace, _records


def render_professional_report_ui() -> None:
    db = PlatformDatabase(); repo = PlatformRepository(db); service = ProfessionalReportService(db)
    org_id = _ensure_workspace(repo)
    projects = _records(repo, "projects", "organization_id=?", (org_id,))
    st.subheader("📄 Professional Reports")
    if not projects:
        st.info("Create a customer/project and save a professional design first.")
        return
    labels = {f'{p["name"]} ({p["id"][-6:]})': p["id"] for p in projects}
    project_id = labels[st.selectbox("Project", list(labels), key="report_project")]
    designs = _records(repo, "designs", "project_id=?", (project_id,))
    if not designs:
        st.info("No saved designs exist for this project.")
        return
    dlabels = {f'{d["name"]} — v{d["version"]} ({d["status"]})': d["id"] for d in designs}
    design_id = dlabels[st.selectbox("Saved design", list(dlabels), key="report_design")]
    if st.button("📄 Generate Professional Engineering Report", type="primary", use_container_width=True, key="generate_saved_design_report"):
        try:
            report = service.generate_for_design(organization_id=org_id, design_id=design_id, persist=True)
            st.session_state["last_generated_report"] = report
            st.success(f"Report generated and registered as {report['report_id']}.")
        except Exception as exc:
            st.error("Professional report generation failed.")
            st.exception(exc)
    report = st.session_state.get("last_generated_report")
    if report and report.get("design_id") == design_id:
        st.download_button("📥 Download Professional PDF", data=report["pdf_bytes"], file_name=report["filename"], mime="application/pdf", use_container_width=True, key="download_professional_report")
