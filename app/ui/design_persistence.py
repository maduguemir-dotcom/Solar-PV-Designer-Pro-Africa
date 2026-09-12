"""UI for saving professional engineering results into project history."""
from __future__ import annotations
from typing import Any, Mapping
import streamlit as st
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.design_persistence_service import DesignPersistenceService
from app.ui.project_management import _ensure_workspace, _records

def render_design_persistence_ui(result: Mapping[str, Any], equipment_selection: Mapping[str, Any] | None = None) -> None:
    db = PlatformDatabase(); repo = PlatformRepository(db); service = DesignPersistenceService(db)
    org_id = _ensure_workspace(repo)
    projects = _records(repo, "projects", "organization_id=?", (org_id,))
    st.subheader("💾 Save Design to Project")
    if not projects:
        st.info("Create a customer/project first from **Customers & Projects**.")
        return
    labels = {f'{p["name"]} ({p["id"][-6:]})': p["id"] for p in projects}
    selected_label = st.selectbox("Project", list(labels), key="design_persistence_project")
    project_id = labels[selected_label]
    designs = _records(repo, "designs", "project_id=?", (project_id,))
    mode = st.radio("Save as", ["Create new design version", "Update existing design"], horizontal=True, key="design_save_mode")
    design_id = None
    if mode == "Update existing design":
        if not designs:
            st.info("No designs exist for this project; create a new version instead.")
            return
        dlabels = {f'{d["name"]} — v{d["version"]} ({d["status"]})': d["id"] for d in designs}
        design_id = dlabels[st.selectbox("Existing design", list(dlabels), key="design_persistence_existing")]
    else:
        default_name = str(result.get("project_name") or "Professional Engineering Design")
        design_name = st.text_input("Design name", value=default_name, key="design_persistence_name")
    if st.button("💾 Save Professional Design", type="primary", use_container_width=True, key="save_professional_design"):
        try:
            saved = service.save_professional_design(organization_id=org_id, project_id=project_id, result=result,
                equipment_selection=equipment_selection, design_id=design_id, design_name=design_name if mode.startswith("Create") else None,
                engine_version=str(result.get("design_version") or "v4"))
            st.session_state["last_saved_design"] = saved
            st.success(f"Design saved successfully — Version {saved['version']}.")
        except Exception as exc:
            st.error("Design could not be saved."); st.exception(exc)
