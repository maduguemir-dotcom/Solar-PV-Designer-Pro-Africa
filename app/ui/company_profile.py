from __future__ import annotations
import streamlit as st
from services.company_profile_service import CompanyProfileService
from platform.database import PlatformDatabase
from platform.repositories import PlatformRepository

def render_company_profile_ui():
    identity = st.session_state.get("authenticated_user", {})
    org_id = st.session_state.get("current_organization_id") or identity.get("organization_id")
    if not org_id:
        st.warning("Select an organization first.")
        return
    repo = PlatformRepository(PlatformDatabase())
    service = CompanyProfileService(repo)
    profile = service.get(org_id)
    st.title("🏢 Company Profile & Branding")
    st.caption("Configure the identity and commercial information used in proposals and reports.")
    with st.form("company_profile_form"):
        c1, c2 = st.columns(2)
        legal = c1.text_input("Legal company name", profile.get("legal_name", ""))
        display = c2.text_input("Display name", profile.get("display_name", ""))
        address = st.text_area("Company address", profile.get("address", ""))
        phone = st.text_input("Phone", profile.get("phone", ""))
        email = st.text_input("Email", profile.get("email", ""))
        website = st.text_input("Website", profile.get("website", ""))
        tax_id = st.text_input("Tax/VAT identification", profile.get("tax_id", ""))
        logo = st.text_input("Logo file path (optional)", profile.get("logo_path", ""))
        validity = st.number_input("Quotation validity (days)", min_value=1, max_value=365, value=int(profile.get("quotation_validity_days") or 30))
        payment = st.text_area("Payment terms", profile.get("payment_terms", ""))
        bank = st.text_area("Bank/payment details", profile.get("bank_details", ""))
        terms = st.text_area("Terms and conditions", profile.get("terms_conditions", ""), height=180)
        if st.form_submit_button("Save Company Profile"):
            service.save(org_id, legal_name=legal, display_name=display, address=address, phone=phone, email=email, website=website, tax_id=tax_id, logo_path=logo, quotation_validity_days=validity, payment_terms=payment, bank_details=bank, terms_conditions=terms)
            st.success("Company profile saved.")
