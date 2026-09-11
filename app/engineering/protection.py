"""Indicative PV/AC protection-device sizing and architecture checks."""
from __future__ import annotations

from typing import Any

STANDARD_PROTECTION_A = (6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400)


def _next_standard(value: float) -> int:
    for rating in STANDARD_PROTECTION_A:
        if rating >= value:
            return rating
    return STANDARD_PROTECTION_A[-1]


def size_pv_overcurrent_protection(
    *,
    module_isc_a: float,
    parallel_strings: int,
    design_margin: float = 1.25,
) -> dict[str, Any]:
    """Provide indicative string and array overcurrent ratings."""
    if module_isc_a <= 0 or parallel_strings <= 0:
        raise ValueError("Module Isc and parallel strings must be greater than zero.")
    if design_margin < 1:
        raise ValueError("Design margin must be at least 1.0.")

    string_protection_a = _next_standard(module_isc_a * design_margin)
    array_current_a = module_isc_a * parallel_strings
    array_protection_a = _next_standard(array_current_a * design_margin)
    return {
        "module_isc_a": module_isc_a,
        "parallel_strings": parallel_strings,
        "string_fuse_rating_a": string_protection_a,
        "array_overcurrent_rating_a": array_protection_a,
        "array_isc_a": array_current_a,
        "datasheet_fuse_limit_check_required": True,
    }


def size_ac_breaker(
    *,
    load_power_w: float,
    system_voltage_v: float,
    power_factor: float = 1.0,
    design_margin: float = 1.25,
) -> dict[str, Any]:
    if load_power_w <= 0 or system_voltage_v <= 0:
        raise ValueError("Load power and system voltage must be greater than zero.")
    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1.")
    current_a = load_power_w / (system_voltage_v * power_factor)
    design_current_a = current_a * design_margin
    return {
        "load_current_a": current_a,
        "design_current_a": design_current_a,
        "recommended_breaker_a": _next_standard(design_current_a),
        "rcd_rcbo_assessment_required": True,
    }


def protection_architecture(*, dc_spd_required: bool = True, ac_spd_required: bool = True) -> dict[str, Any]:
    """Return a design checklist rather than pretending to select final SPD devices."""
    return {
        "dc_isolator_required": True,
        "dc_spd_required": dc_spd_required,
        "ac_main_isolator_or_breaker_required": True,
        "ac_spd_required": ac_spd_required,
        "earthing_bonding_required": True,
        "final_device_selection_requires_code_and_datasheet_review": True,
    }
