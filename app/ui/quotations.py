"""Stage 6B costing and quotation UI."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.quotation_service import CostLine, calculate_quote
from app.services.quotation_persistence_service import QuotationPersistenceService
from app.services.subscription_service import SubscriptionService, UsageLimitError


def render_quotation_ui():
    db = PlatformDatabase()
    repo = PlatformRepository(db)
    org_id = st.session_state.get("current_organization_id")
    if not org_id or not repo.get_one("organizations", org_id):
        st.error("No active organization workspace is available.")
        return

    subscription = SubscriptionService(db)
    projects = repo.list_records("projects", "organization_id=?", (org_id,))
    customers = repo.list_records("customers", "organization_id=?", (org_id,))
    st.title("💼 Costing & Quotations")
    st.caption("Build transparent project costs and customer quotations from your engineering or market inputs.")

    if not projects:
        st.info("Create a project first in Customers & Projects.")
        return

    project_map = {f'{p["name"]} ({p["id"][-6:]})': p for p in projects}
    customer_map = {c["id"]: c["name"] for c in customers}
    project_label = st.selectbox("Project", list(project_map))
    project = project_map[project_label]
    quote_currency = st.selectbox("Quotation currency", ["USD", "NGN", "UGX", "KES", "TZS", "GHS", "ZAR", "EUR", "GBP"])

    if "quote_lines" not in st.session_state:
        st.session_state.quote_lines = []

    with st.form("quotation_line_form", clear_on_submit=True):
        a, b, c = st.columns(3)
        category = a.selectbox("Category", ["Solar Panels", "Battery", "Inverter", "Charge Controller", "Mounting", "Protection", "Cabling", "Labour", "Transport", "Engineering", "Other"])
        description = b.text_input("Description *")
        unit = c.text_input("Unit", value="unit")
        d, e, f = st.columns(3)
        quantity = d.number_input("Quantity", min_value=0.01, value=1.0, step=1.0)
        unit_price = e.number_input("Unit price", min_value=0.0, value=0.0, step=100.0)
        currency = f.selectbox("Source currency", ["USD", "NGN", "UGX", "KES", "TZS", "GHS", "ZAR", "EUR", "GBP"])
        fx = st.number_input("FX rate → quotation currency", min_value=0.000001, value=1.0, format="%.6f", help="Enter how many quotation-currency units equal one source-currency unit. Use 1 when currencies match.")
        if st.form_submit_button("➕ Add cost line", use_container_width=True):
            try:
                line = CostLine(category, description, quantity, unit_price, currency, fx, unit)
                line.validate(quote_currency)
                st.session_state.quote_lines.append(line)
                st.success("Cost line added.")
            except ValueError as exc:
                st.error(str(exc))

    lines = st.session_state.quote_lines
    if lines:
        rows = [line.to_dict(quote_currency) for line in lines]
        st.dataframe(pd.DataFrame(rows)[["category","description","quantity","unit","unit_price","currency","fx_rate","total"]], use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear cost lines", use_container_width=True):
            st.session_state.quote_lines = []
            st.rerun()

    st.markdown("### Commercial adjustments")
    x1, x2, x3, x4 = st.columns(4)
    overhead = x1.number_input("Overhead %", min_value=0.0, value=0.0, step=1.0)
    contingency = x2.number_input("Contingency %", min_value=0.0, value=0.0, step=1.0)
    markup = x3.number_input("Markup %", min_value=0.0, value=15.0, step=1.0)
    tax = x4.number_input("Tax %", min_value=0.0, value=0.0, step=1.0)

    if not lines:
        st.info("Add at least one cost line to calculate a quotation.")
        return
    try:
        quote = calculate_quote(lines, quote_currency=quote_currency, overhead_percent=overhead,
                                contingency_percent=contingency, markup_percent=markup, tax_percent=tax)
    except ValueError as exc:
        st.error(str(exc))
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Direct cost", f'{quote_currency} {quote["direct_cost"]:,.2f}')
    m2.metric("Markup", f'{quote_currency} {quote["markup"]:,.2f}')
    m3.metric("Tax", f'{quote_currency} {quote["tax"]:,.2f}')
    m4.metric("Customer total", f'{quote_currency} {quote["grand_total"]:,.2f}')

    with st.form("save_quote_form"):
        quote_number = st.text_input("Quote number *", value="QT-" + project["id"][-8:].upper())
        status = st.selectbox("Status", ["draft", "issued", "accepted", "rejected", "expired"])
        if st.form_submit_button("💾 Save quotation", use_container_width=True):
            try:
                subscription.record_if_allowed(org_id, "quotations_created", 1)
                qid = QuotationPersistenceService(db).create_quote(
                    org_id, project["id"], quote_number, quote,
                    customer_id=project.get("customer_id"), status=status)
                st.success(f"Quotation saved: {qid[-12:]}")
            except UsageLimitError as exc:
                st.warning(str(exc))

    saved = repo.list_records("quotations", "organization_id=? ORDER BY created_at DESC", (org_id,))
    if saved:
        st.markdown("### Saved quotations")
        st.dataframe(pd.DataFrame([{
            "Quote": q["quote_number"], "Project": project_map.get(next((k for k,v in project_map.items() if v["id"] == q["project_id"]), ""), {}).get("name", "—"),
            "Status": q["status"], "Currency": q["currency"], "Total": q["grand_total"], "Created": q["created_at"]
        } for q in saved]), use_container_width=True, hide_index=True)
