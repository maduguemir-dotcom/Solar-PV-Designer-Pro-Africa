"""Stage 2B electrical design orchestration."""
from __future__ import annotations

from typing import Any

from .pv_electrical import size_pv_strings
from .charge_controller import size_charge_controller
from .cable_sizing import size_cable
from .protection import size_pv_overcurrent_protection, size_ac_breaker, protection_architecture


def run_electrical_design(
    *,
    pv_capacity_kwp: float,
    module_rating_w: float,
    module_voc_v: float,
    module_vmp_v: float,
    module_isc_a: float,
    module_imp_a: float,
    controller_max_pv_voltage_v: float,
    controller_min_mppt_voltage_v: float,
    system_voltage_v: float,
    peak_operating_load_w: float,
    pv_cable_length_m: float,
    battery_cable_length_m: float,
    ac_cable_length_m: float,
    battery_current_a: float,
    ac_voltage_v: float | None = None,
    max_dc_voltage_drop_pct: float = 3.0,
    max_ac_voltage_drop_pct: float = 3.0,
    min_ambient_temp_c: float = 5.0,
    max_ambient_temp_c: float = 45.0,
    design_margin: float = 1.25,
    power_factor: float = 1.0,
) -> dict[str, Any]:
    """Run Stage 2B string, controller, cable and protection calculations."""
    pv = size_pv_strings(
        pv_capacity_kwp=pv_capacity_kwp,
        module_rating_w=module_rating_w,
        voc_v=module_voc_v,
        vmp_v=module_vmp_v,
        isc_a=module_isc_a,
        imp_a=module_imp_a,
        controller_max_pv_voltage_v=controller_max_pv_voltage_v,
        controller_min_mppt_voltage_v=controller_min_mppt_voltage_v,
        min_ambient_temp_c=min_ambient_temp_c,
        max_ambient_temp_c=max_ambient_temp_c,
    )
    controller = size_charge_controller(
        pv_capacity_kwp=pv_capacity_kwp,
        system_voltage_v=system_voltage_v,
        design_margin=design_margin,
        controller_max_pv_voltage_v=controller_max_pv_voltage_v,
        cold_string_voc_v=pv["cold_string_voc_v"],
    )
    pv_cable = size_cable(
        current_a=pv["array_imp_a"],
        one_way_length_m=pv_cable_length_m,
        system_voltage_v=pv["hot_string_vmp_v"],
        max_voltage_drop_pct=max_dc_voltage_drop_pct,
        phase="dc",
    )
    battery_cable = size_cable(
        current_a=battery_current_a,
        one_way_length_m=battery_cable_length_m,
        system_voltage_v=system_voltage_v,
        max_voltage_drop_pct=max_dc_voltage_drop_pct,
        phase="dc",
    )
    ac_voltage = ac_voltage_v or system_voltage_v
    ac_cable = size_cable(
        current_a=peak_operating_load_w / (ac_voltage * power_factor),
        one_way_length_m=ac_cable_length_m,
        system_voltage_v=ac_voltage,
        max_voltage_drop_pct=max_ac_voltage_drop_pct,
        phase="single_phase",
    )
    protection = size_pv_overcurrent_protection(
        module_isc_a=module_isc_a,
        parallel_strings=pv["parallel_strings"],
        design_margin=design_margin,
    )
    protection["ac"] = size_ac_breaker(
        load_power_w=peak_operating_load_w,
        system_voltage_v=ac_voltage,
        power_factor=power_factor,
        design_margin=design_margin,
    )
    protection["architecture"] = protection_architecture()

    return {
        "pv_strings": pv,
        "charge_controller": controller,
        "cables": {"pv_dc": pv_cable, "battery_dc": battery_cable, "ac": ac_cable},
        "protection": protection,
        "engineering_status": "indicative_design_requires_final_datasheet_and_code_review",
    }
