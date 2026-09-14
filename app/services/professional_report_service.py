"""Stage 4D professional report generation and persistence."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Mapping, Optional
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository


class ProfessionalReportService:
    """Build a professional PDF from a saved engineering design and register it."""

    def __init__(self, database: Optional[PlatformDatabase] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)

    @staticmethod
    def _num(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _text(value: Any, default: str = "—") -> str:
        if value is None or value == "":
            return default
        return str(value)

    def _build_pdf(self, *, project: Mapping[str, Any], design: Mapping[str, Any], result: Mapping[str, Any], equipment: list[Mapping[str, Any]]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
        styles = getSampleStyleSheet()
        title = styles["Title"]
        heading = styles["Heading2"]
        body = styles["BodyText"]
        story: list[Any] = []

        story += [Paragraph("Solar PV Designer Pro Africa™", title),
                  Paragraph("Professional Engineering Design Report", styles["Heading1"]), Spacer(1, 5*mm)]
        story.append(Paragraph(f"Project: {self._text(project.get('name'))}", body))
        story.append(Paragraph(f"Design: {self._text(design.get('name'))} — Version {design.get('version', '—')}", body))
        story.append(Paragraph(f"Engineering Engine: {self._text(design.get('engine_version'))}", body))
        story.append(Paragraph("Prepared by: Engr. Prof. Ibrahim Sani Madugu", body))
        story.append(Spacer(1, 7*mm))

        load = result.get("load", {}) or {}
        pv = result.get("pv", {}) or {}
        battery = result.get("battery", {}) or {}
        inverter = result.get("inverter", {}) or {}
        electrical = result.get("electrical", {}) or {}
        validation = result.get("validation", {}) or {}

        def table(rows: list[list[str]]) -> Table:
            t = Table(rows, colWidths=[72*mm, 100*mm], repeatRows=1)
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]))
            return t

        story.append(Paragraph("1. Project & Load Summary", heading))
        story.append(table([
            ["Parameter", "Value"],
            ["Location", self._text(project.get("location"))],
            ["Daily energy demand", f"{self._num(load.get('daily_energy_kwh')):.2f} kWh/day"],
            ["Monthly energy", f"{self._num(load.get('monthly_energy_kwh')):.2f} kWh/month"],
            ["Connected load", f"{self._num(load.get('connected_load_w')):.0f} W"],
            ["Peak operating load", f"{self._num(load.get('diversity_adjusted_peak_w')):.0f} W"],
            ["Surge peak", f"{self._num(load.get('surge_peak_w')):.0f} W"],
        ]))
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("2. PV & Battery Design", heading))
        story.append(table([
            ["Parameter", "Value"],
            ["PV array", f"{self._num(pv.get('pv_capacity_kwp')):.2f} kWp"],
            ["Required PV", f"{self._num(pv.get('required_kwp')):.2f} kWp"],
            ["PV modules", self._text(pv.get("panel_count"), "Calculated by engineering engine")],
            ["Battery nominal capacity", f"{self._num(battery.get('nominal_battery_kwh')):.2f} kWh"],
            ["Battery bank voltage", f"{self._num(battery.get('system_voltage_v')):.0f} V"],
            ["Battery capacity", f"{self._num(battery.get('battery_capacity_ah')):.0f} Ah"],
            ["Autonomy", f"{self._num(battery.get('autonomy_days')):.1f} days"],
        ]))
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("3. Inverter & Electrical Design", heading))
        story.append(table([
            ["Parameter", "Value"],
            ["Recommended continuous inverter", f"{self._num(inverter.get('recommended_continuous_w'))/1000:.2f} kW"],
            ["Recommended surge inverter", f"{self._num(inverter.get('recommended_surge_w'))/1000:.2f} kW"],
            ["PV strings", json.dumps(electrical.get("pv_strings", {}), default=str)],
            ["Charge controller", json.dumps(electrical.get("charge_controller", {}), default=str)],
            ["DC cable design", json.dumps(electrical.get("dc_cable", {}), default=str)],
            ["AC cable design", json.dumps(electrical.get("ac_cable", {}), default=str)],
            ["Protection", json.dumps(electrical.get("protection", {}), default=str)],
        ]))
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("4. Selected Equipment", heading))
        equipment_rows = [["Type", "Product ID", "Quantity"]]
        for item in equipment:
            equipment_rows.append([self._text(item.get("equipment_type")), self._text(item.get("product_id")), str(item.get("quantity", 1))])
        if len(equipment_rows) == 1:
            equipment_rows.append(["No saved equipment", "—", "—"])
        et = Table(equipment_rows, colWidths=[60*mm, 85*mm, 27*mm], repeatRows=1)
        et.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .4, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")]))
        story.append(et)
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("5. Engineering Validation", heading))
        score = result.get("design_quality_score", 0)
        status = self._text(result.get("design_status"), "REVIEW REQUIRED")
        story.append(Paragraph(f"Design status: <b>{status}</b> — Quality score: <b>{self._num(score):.1f}/100</b>", body))
        for warning in validation.get("warnings", []) or []:
            story.append(Paragraph(f"• Warning: {self._text(warning)}", body))
        for error in validation.get("errors", []) or []:
            story.append(Paragraph(f"• Review item: {self._text(error)}", body))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("Assumptions", heading))
        assumptions = result.get("assumptions_register", []) or []
        if assumptions:
            for assumption in assumptions:
                story.append(Paragraph(f"• {self._text(assumption)}", body))
        else:
            story.append(Paragraph("No additional assumptions were recorded.", body))

        story.append(PageBreak())
        story.append(Paragraph("6. Engineering Disclaimer", heading))
        story.append(Paragraph(
            "This report is an engineering design aid and not a substitute for site verification, "
            "manufacturer documentation, structural assessment, electrical code compliance, protection coordination, "
            "or approval by the responsible qualified professional. Final installation decisions must use current "
            "local regulations and applicable standards.", body))
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def generate_for_design(self, *, organization_id: str, design_id: str, persist: bool = True) -> dict[str, Any]:
        design = self.repository.get_one("designs", design_id)
        if not design:
            raise ValueError("Design not found.")
        project = self.repository.get_one("projects", design["project_id"])
        if not project or project.get("organization_id") != organization_id:
            raise ValueError("Design does not belong to the selected organization.")
        rows = self.repository.list_records("design_results", "design_id=? AND result_type=?", (design_id, "engineering"))
        if not rows:
            raise ValueError("No saved engineering result exists for this design.")
        result = json.loads(rows[0]["result_json"])
        equipment = self.repository.list_records("design_equipment", "design_id=?", (design_id,))
        pdf_bytes = self._build_pdf(project=project, design=design, result=result, equipment=equipment)

        report_id = None
        file_path = ""
        if persist:
            report_id = self.repository.create_report(design_id, "engineering", status="generated")
            report_dir = Path(__file__).resolve().parents[1] / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            path = report_dir / f"{report_id}.pdf"
            path.write_bytes(pdf_bytes)
            file_path = str(path)
            self.repository.update_report(report_id, file_path=file_path, status="generated")
            self.repository.record_usage(organization_id, "professional_reports_generated", 1)
        return {"report_id": report_id, "design_id": design_id, "file_path": file_path, "pdf_bytes": pdf_bytes, "filename": f"{design['name'].replace(' ', '_')}_v{design['version']}.pdf"}
