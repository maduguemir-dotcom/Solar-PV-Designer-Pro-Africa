"""Indicative generator sizing for hybrid/off-grid systems."""
from __future__ import annotations
import math


def size_generator(
    *,
    peak_load_w: float,
    battery_charging_power_w: float = 0.0,
    design_margin: float = 1.25,
    generator_power_factor: float = 0.8,
    preferred_loading_fraction: float = 0.80,
) -> dict:
    if peak_load_w < 0 or battery_charging_power_w < 0:
        raise ValueError("Power inputs cannot be negative.")
    if design_margin < 1 or not 0 < generator_power_factor <= 1 or not 0 < preferred_loading_fraction <= 1:
        raise ValueError("Invalid generator design parameters.")
    required_kw = (peak_load_w + battery_charging_power_w) / 1000 * design_margin
    required_kva = required_kw / generator_power_factor
    recommended_kva = required_kva / preferred_loading_fraction
    return {
        "peak_load_kw": peak_load_w / 1000,
        "battery_charging_power_kw": battery_charging_power_w / 1000,
        "required_generator_kw": required_kw,
        "required_generator_kva": required_kva,
        "recommended_generator_kva": math.ceil(recommended_kva * 10) / 10,
        "generator_power_factor": generator_power_factor,
        "preferred_loading_fraction": preferred_loading_fraction,
        "design_margin": design_margin,
    }
