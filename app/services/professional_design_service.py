"""Compatibility service connecting the v3 engineering engine to the existing UI.

This module deliberately keeps Streamlit out of the engineering layer.  It
translates the existing appliance planner records (or the manual daily-energy
input) into the professional engineering engine's load model.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

try:
    from engineering.design_engine_v4 import run_validated_professional_design
    from engineering.load_analysis import LoadItem
except ModuleNotFoundError:  # package import in tests/tooling
    from app.engineering.design_engine_v4 import run_validated_professional_design
    from app.engineering.load_analysis import LoadItem


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_engineering_loads(
    appliance_records: Iterable[Mapping[str, Any]] | None,
    daily_energy_kwh: float,
) -> list[LoadItem]:
    """Convert existing appliance records into Stage 2 load items.

    If no usable appliance records exist, create a transparent aggregate load
    equivalent.  The aggregate uses five operating hours/day and is intended
    only as a design-screening input; users should use the appliance planner
    for a more realistic peak-load model.
    """
    loads: list[LoadItem] = []
    for record in appliance_records or []:
        power = _number(record.get("power_w"), 0.0)
        quantity = max(0.0, _number(record.get("quantity"), 1.0))
        hours = max(0.0, _number(record.get("hours_per_day"), 0.0))
        if power <= 0 or quantity <= 0 or hours <= 0:
            continue
        loads.append(
            LoadItem(
                name=str(record.get("name") or "Appliance"),
                quantity=quantity,
                power_w=power,
                hours_per_day=hours,
                days_per_week=max(0.0, _number(record.get("days_per_week"), 7.0)),
                surge_factor=max(1.0, _number(record.get("surge_factor"), 1.0)),
                is_surge_load=bool(record.get("is_surge_load", False)),
            )
        )

    if loads:
        return loads

    energy = max(0.0, _number(daily_energy_kwh))
    if energy <= 0:
        return []
    # Explicit fallback so the professional engine can still be used when
    # the user chooses manual energy demand instead of the appliance planner.
    return [
        LoadItem(
            name="Aggregate daily load (screening)",
            quantity=1,
            power_w=(energy * 1000.0 / 5.0),
            hours_per_day=5.0,
        )
    ]


def run_ui_professional_design(
    *,
    appliance_records: Iterable[Mapping[str, Any]] | None,
    daily_energy_kwh: float,
    peak_sun_hours: float,
    system_voltage_v: float,
    system_derating: float,
    battery_autonomy_days: float,
    battery_dod: float,
    battery_efficiency: float,
    temperature_c: float = 25.0,
    panel_rating_w: float = 550.0,
    include_generator: bool = False,
    project_name: str = "Solar PV Project",
) -> dict[str, Any]:
    loads = build_engineering_loads(appliance_records, daily_energy_kwh)
    if not loads:
        raise ValueError("No usable electrical load was provided.")

    return run_validated_professional_design(
        loads,
        peak_sun_hours=peak_sun_hours,
        system_voltage_v=system_voltage_v,
        system_derating=system_derating,
        design_margin=1.10,
        battery_autonomy_days=battery_autonomy_days,
        battery_dod=battery_dod,
        battery_efficiency=battery_efficiency,
        panel_rating_w=panel_rating_w,
        temperature_c=temperature_c,
        module_voc_v=49.5,
        module_vmp_v=41.5,
        module_isc_a=14.0,
        module_imp_a=13.3,
        controller_max_pv_voltage_v=150.0,
        controller_min_mppt_voltage_v=60.0,
        pv_cable_length_m=20.0,
        battery_cable_length_m=3.0,
        ac_cable_length_m=20.0,
        ac_voltage_v=230.0,
        include_generator=include_generator,
        project_name=project_name,
    )
