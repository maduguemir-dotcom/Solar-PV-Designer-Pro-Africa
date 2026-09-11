"""DC/AC cable sizing and voltage-drop calculations."""
from __future__ import annotations

from math import sqrt
from typing import Any

STANDARD_CABLE_SIZES_MM2 = (1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240)
COPPER_RESISTIVITY_OHM_MM2_PER_M = 0.0175


def _next_standard_size(required_mm2: float) -> float:
    for size in STANDARD_CABLE_SIZES_MM2:
        if size >= required_mm2:
            return size
    return STANDARD_CABLE_SIZES_MM2[-1]


def size_cable(
    *,
    current_a: float,
    one_way_length_m: float,
    system_voltage_v: float,
    max_voltage_drop_pct: float = 3.0,
    conductor: str = "copper",
    phase: str = "dc",
) -> dict[str, Any]:
    """Calculate conductor area from voltage-drop limit.

    This is a voltage-drop calculation only; ampacity, installation method,
    ambient temperature, grouping and local code requirements must also be
    checked before selecting the final cable.
    """
    if current_a <= 0 or one_way_length_m <= 0 or system_voltage_v <= 0:
        raise ValueError("Current, length and system voltage must be greater than zero.")
    if not 0 < max_voltage_drop_pct < 100:
        raise ValueError("Maximum voltage drop percentage must be between 0 and 100.")
    if conductor.lower() != "copper":
        raise ValueError("Stage 2B currently supports copper conductors only.")

    allowed_drop_v = system_voltage_v * max_voltage_drop_pct / 100.0
    phase_key = phase.lower()
    if phase_key in {"dc", "single_phase", "1ph", "single-phase"}:
        numerator = 2.0 * one_way_length_m * current_a * COPPER_RESISTIVITY_OHM_MM2_PER_M
    elif phase_key in {"three_phase", "3ph", "three-phase"}:
        numerator = sqrt(3.0) * one_way_length_m * current_a * COPPER_RESISTIVITY_OHM_MM2_PER_M
    else:
        raise ValueError("phase must be 'dc', 'single_phase' or 'three_phase'.")

    required_area_mm2 = numerator / allowed_drop_v
    selected_area_mm2 = _next_standard_size(required_area_mm2)
    actual_drop_v = numerator / selected_area_mm2
    actual_drop_pct = actual_drop_v / system_voltage_v * 100.0

    return {
        "current_a": current_a,
        "one_way_length_m": one_way_length_m,
        "system_voltage_v": system_voltage_v,
        "max_voltage_drop_pct": max_voltage_drop_pct,
        "required_area_mm2": required_area_mm2,
        "selected_area_mm2": selected_area_mm2,
        "actual_voltage_drop_v": actual_drop_v,
        "actual_voltage_drop_pct": actual_drop_pct,
        "conductor": conductor,
        "phase": phase,
        "ampacity_check_required": True,
    }
