"""Battery-bank sizing calculations."""

from __future__ import annotations
import math


def size_battery_bank(
    daily_energy_kwh: float,
    autonomy_days: float,
    system_voltage_v: float,
    depth_of_discharge: float = 0.80,
    battery_efficiency: float = 0.90,
    design_margin: float = 1.10,
    battery_unit_voltage_v: float | None = None,
    battery_unit_capacity_ah: float | None = None,
) -> dict:
    """Calculate nominal battery capacity and optional series/parallel count."""
    if daily_energy_kwh <= 0:
        raise ValueError("Daily energy must be greater than zero.")
    if autonomy_days < 0:
        raise ValueError("Autonomy cannot be negative.")
    if system_voltage_v <= 0:
        raise ValueError("System voltage must be greater than zero.")
    if not 0 < depth_of_discharge <= 1:
        raise ValueError("Depth of discharge must be between 0 and 1.")
    if not 0 < battery_efficiency <= 1:
        raise ValueError("Battery efficiency must be between 0 and 1.")
    if design_margin < 1:
        raise ValueError("Design margin must be at least 1.")

    usable_kwh = daily_energy_kwh * autonomy_days * design_margin
    nominal_kwh = usable_kwh / (depth_of_discharge * battery_efficiency)
    nominal_ah = nominal_kwh * 1000.0 / system_voltage_v

    result = {
        "daily_energy_kwh": daily_energy_kwh,
        "autonomy_days": autonomy_days,
        "system_voltage_v": system_voltage_v,
        "depth_of_discharge": depth_of_discharge,
        "battery_efficiency": battery_efficiency,
        "design_margin": design_margin,
        "usable_energy_kwh": usable_kwh,
        "nominal_battery_kwh": nominal_kwh,
        "nominal_battery_ah": nominal_ah,
    }

    if battery_unit_voltage_v is not None and battery_unit_capacity_ah is not None:
        if battery_unit_voltage_v <= 0 or battery_unit_capacity_ah <= 0:
            raise ValueError("Battery unit voltage and capacity must be positive.")
        series = math.ceil(system_voltage_v / battery_unit_voltage_v)
        parallel = math.ceil(nominal_ah / battery_unit_capacity_ah)
        result.update({
            "battery_unit_voltage_v": battery_unit_voltage_v,
            "battery_unit_capacity_ah": battery_unit_capacity_ah,
            "series_units": series,
            "parallel_strings": parallel,
            "total_battery_units": series * parallel,
        })

    return result
