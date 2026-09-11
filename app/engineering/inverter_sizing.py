"""Inverter sizing from load demand rather than PV capacity."""

from __future__ import annotations


def size_inverter(
    peak_operating_w: float,
    peak_surge_w: float | None = None,
    design_margin: float = 1.25,
    power_factor: float = 1.0,
) -> dict:
    """Return recommended inverter real-power and apparent-power capacity."""
    if peak_operating_w <= 0:
        raise ValueError("Peak operating load must be greater than zero.")
    if peak_surge_w is None:
        peak_surge_w = peak_operating_w
    if peak_surge_w < peak_operating_w:
        raise ValueError("Peak surge load cannot be below operating load.")
    if design_margin < 1:
        raise ValueError("Design margin must be at least 1.")
    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be between 0 and 1.")

    continuous_w = peak_operating_w * design_margin
    surge_w = peak_surge_w * design_margin
    continuous_va = continuous_w / power_factor
    surge_va = surge_w / power_factor

    return {
        "peak_operating_w": peak_operating_w,
        "peak_surge_w": peak_surge_w,
        "design_margin": design_margin,
        "power_factor": power_factor,
        "recommended_continuous_w": continuous_w,
        "recommended_surge_w": surge_w,
        "recommended_continuous_va": continuous_va,
        "recommended_surge_va": surge_va,
        "recommended_continuous_kva": continuous_va / 1000.0,
        "recommended_surge_kva": surge_va / 1000.0,
    }
