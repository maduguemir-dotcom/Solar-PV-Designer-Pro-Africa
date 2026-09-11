"""Battery-bank electrical configuration and compatibility checks."""
from __future__ import annotations
import math
from typing import Any


def configure_battery_bank(
    *,
    nominal_battery_ah: float,
    system_voltage_v: float,
    unit_voltage_v: float,
    unit_capacity_ah: float,
    max_continuous_current_a: float,
    recommended_current_margin: float = 1.25,
) -> dict[str, Any]:
    if nominal_battery_ah <= 0 or system_voltage_v <= 0:
        raise ValueError("Battery capacity and system voltage must be positive.")
    if unit_voltage_v <= 0 or unit_capacity_ah <= 0:
        raise ValueError("Battery unit ratings must be positive.")
    if max_continuous_current_a < 0 or recommended_current_margin < 1:
        raise ValueError("Current and margin inputs are invalid.")

    series = math.ceil(system_voltage_v / unit_voltage_v)
    parallel = math.ceil(nominal_battery_ah / unit_capacity_ah)
    total_units = series * parallel
    bank_ah = parallel * unit_capacity_ah
    bank_voltage = series * unit_voltage_v
    design_current = max_continuous_current_a * recommended_current_margin
    current_capacity_ratio = design_current / bank_ah

    return {
        "series_units": series,
        "parallel_strings": parallel,
        "total_battery_units": total_units,
        "bank_voltage_v": bank_voltage,
        "bank_capacity_ah": bank_ah,
        "design_current_a": design_current,
        "design_current_c_rate": current_capacity_ratio,
        "unit_voltage_v": unit_voltage_v,
        "unit_capacity_ah": unit_capacity_ah,
    }


def check_battery_inverter_compatibility(
    *,
    battery_voltage_v: float,
    inverter_min_voltage_v: float | None = None,
    inverter_max_voltage_v: float | None = None,
    inverter_nominal_voltage_v: float | None = None,
) -> dict[str, Any]:
    if battery_voltage_v <= 0:
        raise ValueError("Battery voltage must be positive.")
    warnings: list[str] = []
    errors: list[str] = []
    if inverter_min_voltage_v is not None and battery_voltage_v < inverter_min_voltage_v:
        errors.append("Battery voltage is below the inverter minimum DC voltage.")
    if inverter_max_voltage_v is not None and battery_voltage_v > inverter_max_voltage_v:
        errors.append("Battery voltage exceeds the inverter maximum DC voltage.")
    if inverter_nominal_voltage_v is not None and abs(battery_voltage_v - inverter_nominal_voltage_v) > 0.15 * inverter_nominal_voltage_v:
        warnings.append("Battery voltage differs materially from the inverter nominal voltage; verify compatibility.")
    return {"compatible": not errors, "warnings": warnings, "errors": errors}
