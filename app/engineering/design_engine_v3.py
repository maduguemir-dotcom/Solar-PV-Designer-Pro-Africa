"""Stage 2C unified professional engineering design orchestration."""
from __future__ import annotations
from typing import Iterable, Mapping, Any
from .load_analysis import LoadItem, analyze_loads
from .pv_sizing import size_pv_array, panel_count
from .battery_sizing import size_battery_bank
from .inverter_sizing import size_inverter
from .electrical_design import run_electrical_design
from .battery_electrical import configure_battery_bank, check_battery_inverter_compatibility
from .generator_sizing import size_generator
from .system_architecture import build_system_architecture
from .design_result import EngineeringDesignResult


def run_professional_design(
    loads: Iterable[LoadItem | Mapping[str, Any]], *,
    peak_sun_hours: float, system_voltage_v: float = 48.0,
    system_derating: float = 0.80, design_margin: float = 1.10,
    battery_autonomy_days: float = 2.0, battery_dod: float = 0.80,
    battery_efficiency: float = 0.90, panel_rating_w: float = 550.0,
    diversity_factor: float = 1.0, temperature_c: float = 25.0,
    power_factor: float = 1.0, module_voc_v: float = 49.5,
    module_vmp_v: float = 41.5, module_isc_a: float = 14.0,
    module_imp_a: float = 13.3, controller_max_pv_voltage_v: float = 150.0,
    controller_min_mppt_voltage_v: float = 60.0, pv_cable_length_m: float = 20.0,
    battery_cable_length_m: float = 3.0, ac_cable_length_m: float = 20.0,
    battery_unit_voltage_v: float | None = None, battery_unit_capacity_ah: float | None = None,
    battery_charging_power_w: float = 0.0, ac_voltage_v: float = 230.0,
    include_generator: bool = False, project_name: str = "Untitled Project",
) -> dict[str, Any]:
    load = analyze_loads(loads, diversity_factor=diversity_factor)
    pv = size_pv_array(load["daily_energy_kwh"], peak_sun_hours, system_derating=system_derating, design_margin=design_margin, temperature_c=temperature_c)
    pv["panel_rating_w"] = panel_rating_w
    pv["panel_count"] = panel_count(pv["pv_capacity_kwp"], panel_rating_w)
    battery = size_battery_bank(load["daily_energy_kwh"], battery_autonomy_days, system_voltage_v, depth_of_discharge=battery_dod, battery_efficiency=battery_efficiency, design_margin=design_margin, battery_unit_voltage_v=battery_unit_voltage_v, battery_unit_capacity_ah=battery_unit_capacity_ah)
    inverter = size_inverter(load["peak_operating_load_w"], load["peak_surge_load_w"], design_margin=design_margin, power_factor=power_factor)
    battery_current = inverter["recommended_continuous_w"] / (system_voltage_v * power_factor) if system_voltage_v else 0.0
    electrical = run_electrical_design(pv_capacity_kwp=pv["pv_capacity_kwp"], module_rating_w=panel_rating_w, module_voc_v=module_voc_v, module_vmp_v=module_vmp_v, module_isc_a=module_isc_a, module_imp_a=module_imp_a, controller_max_pv_voltage_v=controller_max_pv_voltage_v, controller_min_mppt_voltage_v=controller_min_mppt_voltage_v, system_voltage_v=system_voltage_v, peak_operating_load_w=load["peak_operating_load_w"], pv_cable_length_m=pv_cable_length_m, battery_cable_length_m=battery_cable_length_m, ac_cable_length_m=ac_cable_length_m, battery_current_a=battery_current, ac_voltage_v=ac_voltage_v, design_margin=design_margin, power_factor=power_factor, min_ambient_temp_c=5.0, max_ambient_temp_c=45.0)
    battery_electrical = {}
    if battery_unit_voltage_v and battery_unit_capacity_ah:
        battery_electrical = configure_battery_bank(nominal_battery_ah=battery["nominal_battery_ah"], system_voltage_v=system_voltage_v, unit_voltage_v=battery_unit_voltage_v, unit_capacity_ah=battery_unit_capacity_ah, max_continuous_current_a=battery_current)
    compatibility = check_battery_inverter_compatibility(battery_voltage_v=system_voltage_v)
    generator = size_generator(peak_load_w=load["peak_surge_load_w"], battery_charging_power_w=battery_charging_power_w, design_margin=design_margin, generator_power_factor=0.8) if include_generator else {}
    architecture = build_system_architecture(system_voltage_v=system_voltage_v, ac_voltage_v=ac_voltage_v, include_generator=include_generator)
    warnings = compatibility["warnings"]
    errors = compatibility["errors"]
    result = EngineeringDesignResult(project_name=project_name, load=load, pv=pv, battery={**battery, "electrical_configuration": battery_electrical}, inverter=inverter, electrical=electrical, generator=generator, architecture=architecture, warnings=warnings, errors=errors)
    return result.to_dict()
