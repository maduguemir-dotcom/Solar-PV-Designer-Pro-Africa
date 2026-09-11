"""Validation helpers for Stage 2B electrical design."""
from __future__ import annotations


def validate_electrical_design(design: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    controller = design.get("charge_controller", {})
    if controller and not controller.get("voltage_check_pass", True):
        errors.append("PV string cold Voc exceeds the charge controller PV voltage limit.")
    for name, cable in design.get("cables", {}).items():
        if cable.get("actual_voltage_drop_pct", 0) > cable.get("max_voltage_drop_pct", 100):
            errors.append(f"{name} cable exceeds the configured voltage-drop limit.")
        if cable.get("ampacity_check_required"):
            warnings.append(f"{name} cable requires an ampacity/installation-method check.")
    warnings.extend([
        "Verify module temperature coefficients against the exact manufacturer datasheet.",
        "Verify MPPT operating window and maximum PV input current/voltage against the exact controller datasheet.",
        "Verify cable ampacity, insulation, installation method, ambient temperature and grouping.",
        "Verify protective-device ratings, breaking capacity, earthing and SPD requirements against the applicable local code.",
    ])
    return {"valid": not errors, "errors": errors, "warnings": warnings}
