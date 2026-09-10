"""Application service for PV system design.

Stage 1A deliberately preserves the existing v2.4 engineering functions.
The service adapts the Streamlit inputs to their current signatures so that
UI code no longer has to know the calculation API.
"""

from __future__ import annotations

from typing import Any, Dict

from calculations import (
    calculate_battery,
    calculate_carbon,
    calculate_inverter,
    calculate_panels,
    calculate_pv_size,
)


def calculate_system_design(
    *,
    energy_demand: float,
    sun_hours: float,
    system_derating: float,
    temperature: float = 25.0,
    battery_type: str = "Lithium-ion",
    panel_rating_w: float = 550.0,
) -> Dict[str, Any]:
    """Run the currently supported v2.4 design calculations.

    Note:
        system_derating is passed to the existing PV calculation as its
        efficiency/derating factor. Battery autonomy and battery chemistry
        are handled by the legacy battery function in this stabilization
        stage. System voltage, battery efficiency and user-entered DoD are
        retained by the UI for the next engineering-engine upgrade rather
        than silently changing the legacy calculation.
    """
    if energy_demand <= 0:
        raise ValueError("Daily energy demand must be greater than zero.")
    if sun_hours <= 0:
        raise ValueError("Peak Sun Hours must be greater than zero.")
    if not 0 < system_derating <= 1:
        raise ValueError("System derating factor must be between 0 and 1.")
    if panel_rating_w <= 0:
        raise ValueError("Panel rating must be greater than zero.")

    pv_size = calculate_pv_size(
        energy_demand,
        sun_hours,
        system_derating,
        temperature,
    )

    panel_result = calculate_panels(pv_size, panel_rating_w)

    inverter_result = calculate_inverter(pv_size)

    carbon_result = calculate_carbon(energy_demand)

    return {
        "energy_demand": float(energy_demand),
        "sun_hours": float(sun_hours),
        "temperature": float(temperature),
        "system_derating": float(system_derating),
        "battery_type": battery_type,
        "panel_rating_w": float(panel_rating_w),
        "pv_size": pv_size,
        "panel_result": panel_result,
        "inverter_result": inverter_result,
        "carbon_result": carbon_result,
    }


def add_battery_result(
    design: Dict[str, Any],
    *,
    autonomy_days: float,
) -> Dict[str, Any]:
    """Add the legacy battery calculation to an existing design result."""
    if autonomy_days < 0:
        raise ValueError("Battery autonomy cannot be negative.")

    result = dict(design)
    result["autonomy_days"] = float(autonomy_days)
    result["battery_result"] = calculate_battery(
        result["energy_demand"],
        autonomy_days,
        result["battery_type"],
    )
    return result
