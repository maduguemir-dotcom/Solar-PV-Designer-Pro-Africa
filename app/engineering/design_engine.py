"""Orchestration layer for the professional engineering calculations."""

from __future__ import annotations

from typing import Iterable, Mapping, Any

from .load_analysis import LoadItem, analyze_loads
from .pv_sizing import size_pv_array, panel_count
from .battery_sizing import size_battery_bank
from .inverter_sizing import size_inverter


def run_engineering_design(
    loads: Iterable[LoadItem | Mapping[str, Any]],
    *,
    peak_sun_hours: float,
    system_voltage_v: float = 48.0,
    system_derating: float = 0.80,
    design_margin: float = 1.10,
    battery_autonomy_days: float = 2.0,
    battery_dod: float = 0.80,
    battery_efficiency: float = 0.90,
    panel_rating_w: float = 550.0,
    diversity_factor: float = 1.0,
    temperature_c: float = 25.0,
    power_factor: float = 1.0,
) -> dict:
    """Run Stage 2A's load, PV, battery and inverter design basis."""
    load = analyze_loads(loads, diversity_factor=diversity_factor)

    pv = size_pv_array(
        load["daily_energy_kwh"],
        peak_sun_hours,
        system_derating=system_derating,
        design_margin=design_margin,
        temperature_c=temperature_c,
    )
    pv["panel_rating_w"] = panel_rating_w
    pv["panel_count"] = panel_count(pv["pv_capacity_kwp"], panel_rating_w)

    battery = size_battery_bank(
        load["daily_energy_kwh"],
        battery_autonomy_days,
        system_voltage_v,
        depth_of_discharge=battery_dod,
        battery_efficiency=battery_efficiency,
        design_margin=design_margin,
    )

    inverter = size_inverter(
        load["peak_operating_load_w"],
        load["peak_surge_load_w"],
        design_margin=design_margin,
        power_factor=power_factor,
    )

    return {
        "load": load,
        "pv": pv,
        "battery": battery,
        "inverter": inverter,
        "design_basis": {
            "system_voltage_v": system_voltage_v,
            "peak_sun_hours": peak_sun_hours,
            "system_derating": system_derating,
            "design_margin": design_margin,
            "battery_autonomy_days": battery_autonomy_days,
            "battery_dod": battery_dod,
            "battery_efficiency": battery_efficiency,
            "panel_rating_w": panel_rating_w,
            "diversity_factor": diversity_factor,
            "temperature_c": temperature_c,
            "power_factor": power_factor,
        },
    }
