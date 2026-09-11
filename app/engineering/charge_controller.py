"""Charge-controller sizing for battery-based PV systems."""
from __future__ import annotations

from typing import Any


def size_charge_controller(
    *,
    pv_capacity_kwp: float,
    system_voltage_v: float,
    design_margin: float = 1.25,
    controller_max_pv_voltage_v: float | None = None,
    cold_string_voc_v: float | None = None,
    controller_efficiency: float = 0.95,
) -> dict[str, Any]:
    """Size the minimum nominal MPPT charge-controller current.

    The current estimate is PV power converted to battery voltage, with a
    design margin. Datasheet maximum PV voltage/current must still be checked.
    """
    if pv_capacity_kwp <= 0 or system_voltage_v <= 0:
        raise ValueError("PV capacity and system voltage must be greater than zero.")
    if design_margin < 1:
        raise ValueError("Design margin must be at least 1.0.")
    if not 0 < controller_efficiency <= 1:
        raise ValueError("Controller efficiency must be between 0 and 1.")

    required_current_a = pv_capacity_kwp * 1000.0 / system_voltage_v / controller_efficiency
    design_current_a = required_current_a * design_margin
    voltage_ok = True
    voltage_margin_v = None
    if controller_max_pv_voltage_v is not None and cold_string_voc_v is not None:
        voltage_margin_v = controller_max_pv_voltage_v - cold_string_voc_v
        voltage_ok = voltage_margin_v > 0

    return {
        "pv_capacity_kwp": pv_capacity_kwp,
        "system_voltage_v": system_voltage_v,
        "required_current_a": required_current_a,
        "design_current_a": design_current_a,
        "recommended_controller_current_a": design_current_a,
        "controller_max_pv_voltage_v": controller_max_pv_voltage_v,
        "cold_string_voc_v": cold_string_voc_v,
        "voltage_margin_v": voltage_margin_v,
        "voltage_check_pass": voltage_ok,
    }
