"""Validation and engineering warnings for Stage 2A."""

from __future__ import annotations


def validate_design(design: dict) -> list[dict]:
    """Return non-fatal warnings/errors from a completed design."""
    messages = []
    load = design.get("load", {})
    pv = design.get("pv", {})
    battery = design.get("battery", {})
    inverter = design.get("inverter", {})

    if load.get("daily_energy_kwh", 0) <= 0:
        messages.append({"level": "error", "code": "LOAD_ZERO",
                         "message": "Daily energy demand is zero."})

    if pv.get("panel_count", 0) <= 0:
        messages.append({"level": "error", "code": "PV_ZERO",
                         "message": "No PV modules are required by the current inputs."})

    if battery.get("nominal_battery_kwh", 0) <= 0:
        messages.append({"level": "error", "code": "BATTERY_ZERO",
                         "message": "Battery capacity is zero or invalid."})

    if inverter.get("recommended_continuous_w", 0) < load.get("peak_operating_load_w", 0):
        messages.append({"level": "error", "code": "INVERTER_UNDERSIZE",
                         "message": "Recommended inverter continuous capacity is below peak operating load."})

    return messages
