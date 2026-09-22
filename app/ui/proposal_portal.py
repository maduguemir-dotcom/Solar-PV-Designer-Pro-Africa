"""Streamlit UI for proposal delivery and customer portal administration."""
from __future__ import annotations
import streamlit as st
from app.services.proposal_portal_service import ProposalPortalService
from app.platform.database import PlatformDatabase

def render_proposal_portal_ui():
    st.title("🔗 Proposal Portal & Delivery")
    st.caption("Manage proposal status and create secure customer access links.")
    identity = st.session_state.get("authenticated_user") or {}
    org_id = st.session_state.get("current_organization_id") or identity.get("organization_id")
    if not org_id:
        st.warning("Sign in and select an organization first.")
        return
    service = ProposalPortalService(PlatformDatabase())
    quotations = service.repo.list_quotations(org_id)
    if not quotations:
        st.info("No quotations are available yet.")
        return
    labels = {f"{q.get('quote_number') or q['id']} — {q.get('status','draft')}": q for q in quotations}
    selected = st.selectbox("Quotation", list(labels))
    quote = labels[selected]
    status = st.selectbox("Proposal status", ProposalPortalService.STATUSES, index=ProposalPortalService.STATUSES.index(quote.get("status", "draft")) if quote.get("status") in ProposalPortalService.STATUSES else 0)
    if st.button("Update status"):
        service.set_status(quote["id"], org_id, status)
        st.success("Proposal status updated.")
    storage_path = st.text_input("Generated PDF storage path", value="")
    expires_at = st.text_input("Expiry timestamp (optional ISO format)", value="")
    if st.button("Create secure access link"):
        if not storage_path.strip():
            st.error("Provide the generated PDF storage path.")
        else:
            result = service.create_share_link(org_id, quote["id"], storage_path.strip(), expires_at.strip() or None)
            st.success("Secure access token created. Store it safely; it is shown only once.")
            st.code(f"Document ID: {result['document_id']}\nAccess token: {result['access_token']}")
