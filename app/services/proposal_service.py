"""Stage 6C professional quotation/proposal PDF generation."""
from __future__ import annotations
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from app.services.branding_service import company_display_name, company_contact_lines, resolve_logo


def build_proposal_pdf(path: str | Path, *, company: dict, customer: dict, project: dict,
                       quote: dict, quote_number: str, prepared_by: str = "") -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = []
    logo = resolve_logo(company)
    if logo:
        try: story.append(Image(logo, width=35*mm, height=20*mm, kind="proportional"))
        except Exception: pass
    story.append(Paragraph(company_display_name(company), styles["Title"]))
    for line in company_contact_lines(company): story.append(Paragraph(line, styles["BodyText"]))
    story += [Paragraph("Professional Solar Project Quotation", styles["Heading2"]), Spacer(1, 8)]
    info = [
        ["Quotation number", quote_number, "Date", str(date.today())],
        ["Customer", customer.get("name", "—"), "Project", project.get("name", "—")],
        ["Site", project.get("site_name", "—"), "Prepared by", prepared_by or "—"],
    ]
    t = Table(info, colWidths=[32*mm, 62*mm, 30*mm, 56*mm])
    t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .4, colors.grey), ("BACKGROUND", (0,0), (0,-1), colors.lightgrey), ("BACKGROUND", (2,0), (2,-1), colors.lightgrey), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story += [t, Spacer(1, 12), Paragraph("Cost breakdown", styles["Heading2"])]
    rows = [["Category", "Description", "Qty", "Unit", "Total"]]
    for line in quote.get("lines", []):
        rows.append([line.get("category", ""), line.get("description", ""), str(line.get("quantity", "")), line.get("unit", ""), f'{quote["quote_currency"]} {line.get("total", 0):,.2f}'])
    rows += [["", "Direct cost", "", "", f'{quote["quote_currency"]} {quote.get("direct_cost", 0):,.2f}'], ["", "Overhead", "", "", f'{quote["quote_currency"]} {quote.get("overhead", 0):,.2f}'], ["", "Contingency", "", "", f'{quote["quote_currency"]} {quote.get("contingency", 0):,.2f}'], ["", "Markup", "", "", f'{quote["quote_currency"]} {quote.get("markup", 0):,.2f}'], ["", "Tax", "", "", f'{quote["quote_currency"]} {quote.get("tax", 0):,.2f}'], ["", "GRAND TOTAL", "", "", f'{quote["quote_currency"]} {quote.get("grand_total", 0):,.2f}']]
    table = Table(rows, colWidths=[28*mm, 78*mm, 18*mm, 18*mm, 38*mm], repeatRows=1)
    table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .35, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTNAME", (1,-1), (-1,-1), "Helvetica-Bold"), ("BACKGROUND", (1,-1), (-1,-1), colors.whitesmoke), ("ALIGN", (2,1), (-1,-1), "RIGHT")]))
    story += [table, Spacer(1, 14), Paragraph("Terms and conditions", styles["Heading2"]), Paragraph(company.get("terms", "This quotation is subject to final site verification, equipment availability, and mutually agreed payment terms."), styles["BodyText"]), Spacer(1, 18), Paragraph("Acceptance signature: ________________________________", styles["BodyText"])]
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm).build(story)
    return str(output)
