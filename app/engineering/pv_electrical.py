"""PV module electrical and string-sizing calculations.

Stage 2B adds indicative electrical checks without changing the existing UI.
Values are design calculations and must be checked against the selected
module/controller datasheets and the applicable electrical code.
"""
from __future__ import annotations

from math import floor
from typing import Any


def size_pv_strings(
    *,
    pv_capacity_kwp: float,
    module_rating_w: float,
    voc_v: float,
    vmp_v: float,
    isc_a: float,
    imp_a: float,
    controller_max_pv_voltage_v: float,
    controller_min_mppt_voltage_v: float,
    min_ambient_temp_c: float = 5.0,
    max_ambient_temp_c: float = 45.0,
    voc_temp_coeff_pct_per_c: float = -0.29,
    vmp_temp_coeff_pct_per_c: float = -0.30,
) -> dict[str, Any]:
    """Determine practical series/parallel PV module arrangement.

    Temperature coefficients are entered as percent per degree C, normally
    negative for voltage. The calculation uses a conservative cold Voc check
    and hot Vmp check. Parallel strings are then selected to meet the target
    array power.
    """
    values = {
        "pv_capacity_kwp": pv_capacity_kwp,
        "module_rating_w": module_rating_w,
        "voc_v": voc_v,
        "vmp_v": vmp_v,
        "isc_a": isc_a,
        "imp_a": imp_a,
        "controller_max_pv_voltage_v": controller_max_pv_voltage_v,
        "controller_min_mppt_voltage_v": controller_min_mppt_voltage_v,
    }
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero.")
    if controller_min_mppt_voltage_v >= controller_max_pv_voltage_v:
        raise ValueError("Controller MPPT minimum voltage must be below maximum PV voltage.")

    cold_delta = min_ambient_temp_c - 25.0
    hot_delta = max_ambient_temp_c - 25.0
    cold_voc_factor = 1.0 + (voc_temp_coeff_pct_per_c / 100.0) * cold_delta
    hot_vmp_factor = 1.0 + (vmp_temp_coeff_pct_per_c / 100.0) * hot_delta
    cold_voc_module = voc_v * cold_voc_factor
    hot_vmp_module = vmp_v * hot_vmp_factor

    max_series_by_voltage = floor(controller_max_pv_voltage_v / cold_voc_module)
    min_series_by_mppt = 1 if hot_vmp_module >= controller_min_mppt_voltage_v else int(
        (controller_min_mppt_voltage_v + hot_vmp_module - 1) // hot_vmp_module
    )
    if max_series_by_voltage < min_series_by_mppt:
        raise ValueError(
            "No valid module series count satisfies both cold Voc and hot MPPT voltage limits."
        )

    modules_required = max(1, int((pv_capacity_kwp * 1000 + module_rating_w - 1) // module_rating_w))
    series_modules = min_series_by_mppt
    parallel_strings = (modules_required + series_modules - 1) // series_modules
    total_modules = series_modules * parallel_strings
    actual_kwp = total_modules * module_rating_w / 1000.0

    return {
        "required_modules": modules_required,
        "series_modules": series_modules,
        "parallel_strings": parallel_strings,
        "total_modules": total_modules,
        "actual_pv_kwp": actual_kwp,
        "cold_voc_per_module_v": cold_voc_module,
        "cold_string_voc_v": cold_voc_module * series_modules,
        "hot_vmp_per_module_v": hot_vmp_module,
        "hot_string_vmp_v": hot_vmp_module * series_modules,
        "string_operating_current_a": imp_a,
        "array_isc_a": isc_a * parallel_strings,
        "array_imp_a": imp_a * parallel_strings,
        "max_series_by_voltage": max_series_by_voltage,
        "min_series_by_mppt": min_series_by_mppt,
        "controller_voltage_margin_v": controller_max_pv_voltage_v - cold_voc_module * series_modules,
    }
