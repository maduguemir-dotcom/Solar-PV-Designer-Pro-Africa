"""PV array sizing calculations."""

from __future__ import annotations


def size_pv_array(
    daily_energy_kwh: float,
    peak_sun_hours: float,
    system_derating: float = 0.80,
    design_margin: float = 1.10,
    temperature_c: float = 25.0,
    temperature_coefficient_per_c: float = 0.005,
    reference_temperature_c: float = 25.0,
) -> dict:
    """Size PV capacity in kWp.

    The derating factor represents the usable fraction of incident PV
    production. Temperature correction is applied when temperature exceeds
    the reference temperature.

    This is a design-basis calculation; location-specific irradiation and
    module electrical characteristics will be incorporated in later stages.
    """
    if daily_energy_kwh <= 0:
        raise ValueError("Daily energy must be greater than zero.")
    if peak_sun_hours <= 0:
        raise ValueError("Peak Sun Hours must be greater than zero.")
    if not 0 < system_derating <= 1:
        raise ValueError("System derating must be between 0 and 1.")
    if design_margin < 1:
        raise ValueError("Design margin must be at least 1.")
    if temperature_coefficient_per_c < 0:
        raise ValueError("Temperature coefficient cannot be negative.")

    temperature_factor = 1.0
    if temperature_c > reference_temperature_c:
        temperature_factor += (
            temperature_c - reference_temperature_c
        ) * temperature_coefficient_per_c

    base_kwp = daily_energy_kwh / (peak_sun_hours * system_derating)
    required_kwp = base_kwp * design_margin * temperature_factor

    return {
        "daily_energy_kwh": daily_energy_kwh,
        "peak_sun_hours": peak_sun_hours,
        "system_derating": system_derating,
        "design_margin": design_margin,
        "temperature_c": temperature_c,
        "temperature_factor": temperature_factor,
        "pv_capacity_kwp": required_kwp,
    }


def panel_count(pv_capacity_kwp: float, panel_rating_w: float) -> int:
    """Return the minimum whole number of modules required."""
    if pv_capacity_kwp <= 0 or panel_rating_w <= 0:
        raise ValueError("PV capacity and panel rating must be greater than zero.")
    import math
    return math.ceil(pv_capacity_kwp * 1000.0 / panel_rating_w)
