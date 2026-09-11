"""Stage 2D engineering validation and design-quality intelligence."""
from __future__ import annotations
from typing import Any


def _get(d: dict, *keys, default=None):
    cur = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def validate_professional_design(design: dict[str, Any], *, limits: dict[str, float] | None = None) -> dict[str, Any]:
    """Run non-fatal engineering sanity checks over a Stage 2C design result.

    The checks are screening tools, not a substitute for final equipment
    datasheets, local code review, protection coordination or a licensed
    engineer's approval.
    """
    limits = limits or {}
    warnings: list[str] = []
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, message: str, severity: str = "warning"):
        checks.append({"name": name, "passed": passed, "severity": severity, "message": message})
        if not passed:
            (errors if severity == "error" else warnings).append(message)

    load = design.get("load", {})
    pv = design.get("pv", {})
    battery = design.get("battery", {})
    inverter = design.get("inverter", {})
    electrical = design.get("electrical", {})

    daily = float(load.get("daily_energy_kwh", 0) or 0)
    pv_kwp = float(pv.get("pv_capacity_kwp", 0) or 0)
    panel_count = int(pv.get("panel_count", 0) or 0)
    inv_w = float(inverter.get("recommended_continuous_w", 0) or 0)
    peak_w = float(load.get("peak_operating_load_w", 0) or 0)
    surge_w = float(load.get("peak_surge_load_w", 0) or 0)

    check("load_present", daily > 0, "Daily energy demand must be greater than zero.", "error")
    check("pv_present", pv_kwp > 0 and panel_count > 0, "PV design must contain a positive array and panel count.", "error")
    check("inverter_continuous", inv_w >= peak_w, "Inverter continuous rating is below peak operating load.", "error")
    check("inverter_surge", float(inverter.get("recommended_surge_w", 0) or 0) >= surge_w, "Inverter surge capability is below the calculated surge load.", "error")

    ratio = (pv_kwp * 1000 / inv_w) if inv_w > 0 else 0
    min_ratio = float(limits.get("min_pv_inverter_ratio", 0.5))
    max_ratio = float(limits.get("max_pv_inverter_ratio", 1.5))
    check("pv_inverter_ratio", inv_w > 0 and min_ratio <= ratio <= max_ratio,
          f"PV-to-inverter ratio is {ratio:.2f}; verify it is appropriate for the selected inverter and operating strategy.")

    strings = electrical.get("pv_strings", {})
    cold_voc = float(strings.get("cold_string_voc_v", 0) or 0)
    controller_max = float(electrical.get("charge_controller", {}).get("controller_max_pv_voltage_v", 0) or 0)
    if controller_max > 0:
        check("mppt_voltage_window", cold_voc < controller_max,
              "Cold-condition PV string Voc exceeds the charge-controller maximum PV voltage.", "error")

    controller = electrical.get("charge_controller", {})
    check("charge_controller_voltage", controller.get("voltage_check_pass", True),
          "Charge-controller PV voltage check did not pass.", "error")

    cables = electrical.get("cables", {})
    max_drop = float(limits.get("max_voltage_drop_pct", 3.0))
    for key, label in (("pv_dc", "PV DC"), ("battery_dc", "battery DC"), ("ac", "AC")):
        cable = cables.get(key, {})
        if cable:
            actual = float(cable.get("actual_voltage_drop_pct", 999) or 999)
            check(f"{key}_voltage_drop", actual <= max_drop,
                  f"{label} voltage drop is {actual:.2f}%, above the {max_drop:.1f}% screening limit.")

    batt_cfg = battery.get("electrical_configuration", {})
    c_rate = batt_cfg.get("design_current_c_rate")
    max_c = float(limits.get("max_battery_design_c_rate", 0.25))
    if c_rate is not None:
        check("battery_c_rate", float(c_rate) <= max_c,
              f"Battery design current is {float(c_rate):.3f}C; verify the selected battery permits this continuous rate.")

    protection = electrical.get("protection", {})
    check("protection_review", bool(protection), "Protection architecture is missing; complete overcurrent, isolation, SPD and earthing review.", "error")

    score = calculate_design_quality_score(checks)
    status = "PASS" if not errors else "REVIEW REQUIRED"
    if warnings and not errors:
        status = "PASS WITH WARNINGS"
    return {"status": status, "score": score, "checks": checks, "warnings": warnings, "errors": errors}


def calculate_design_quality_score(checks: list[dict[str, Any]]) -> float:
    """Return a 0-100 screening score, weighted toward error-level checks."""
    if not checks:
        return 0.0
    total = 0.0
    earned = 0.0
    for item in checks:
        weight = 2.0 if item.get("severity") == "error" else 1.0
        total += weight
        if item.get("passed"):
            earned += weight
    return round(100.0 * earned / total, 1) if total else 0.0


def build_assumptions_register(*, system_voltage_v: float, ac_voltage_v: float, peak_sun_hours: float,
                               system_derating: float, design_margin: float, battery_dod: float,
                               battery_efficiency: float) -> list[dict[str, Any]]:
    return [
        {"parameter": "Battery/DC bus voltage", "value": system_voltage_v, "unit": "V", "note": "Confirm equipment nominal voltage compatibility."},
        {"parameter": "AC voltage", "value": ac_voltage_v, "unit": "V", "note": "Confirm local supply and inverter output standard."},
        {"parameter": "Peak sun hours", "value": peak_sun_hours, "unit": "h/day", "note": "Use a defensible location-specific solar resource dataset."},
        {"parameter": "System derating", "value": system_derating, "unit": "fraction", "note": "Represents aggregate losses; refine for the final design."},
        {"parameter": "Design margin", "value": design_margin, "unit": "factor", "note": "Engineering margin; final values depend on equipment and project criteria."},
        {"parameter": "Battery depth of discharge", "value": battery_dod, "unit": "fraction", "note": "Must comply with the selected battery manufacturer's limits."},
        {"parameter": "Battery efficiency", "value": battery_efficiency, "unit": "fraction", "note": "Use manufacturer data where available."},
    ]
