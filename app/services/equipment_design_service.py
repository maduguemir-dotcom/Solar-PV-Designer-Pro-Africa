"""Service layer for equipment-aware professional design inputs.

The service converts user/product-library specifications into validated,
machine-readable design inputs. It does not depend on Streamlit.
"""
from __future__ import annotations
from typing import Any, Mapping
try:
    from engineering.pv_electrical import size_pv_strings
    from equipment.schemas import PVModuleSpec, BatterySpec, InverterSpec, ChargeControllerSpec
    from equipment.selection import validate_equipment_selection
except ModuleNotFoundError:
    from app.engineering.pv_electrical import size_pv_strings
    from app.equipment.schemas import PVModuleSpec, BatterySpec, InverterSpec, ChargeControllerSpec
    from app.equipment.selection import validate_equipment_selection
from .professional_design_service import run_ui_professional_design


def _obj(cls, value, defaults):
    if value is None:
        return cls(**defaults)
    if isinstance(value, cls):
        return value
    if isinstance(value, Mapping):
        return cls(**dict(value))
    raise TypeError(f"Expected {cls.__name__}, mapping, or None.")


def run_equipment_aware_design(*, appliance_records, daily_energy_kwh, peak_sun_hours,
                               system_voltage_v, system_derating, battery_autonomy_days,
                               battery_dod, battery_efficiency, temperature_c=25.0,
                               pv_module=None, battery=None, inverter=None,
                               charge_controller=None, include_generator=False,
                               project_name="Solar PV Project") -> dict[str, Any]:
    pv = _obj(PVModuleSpec, pv_module, {})
    batt = _obj(BatterySpec, battery, {})
    inv = _obj(InverterSpec, inverter, {})
    cc = _obj(ChargeControllerSpec, charge_controller, {}) if charge_controller is not False else None

    equipment_check = validate_equipment_selection(
        pv_module=pv, battery=batt, inverter=inv, charge_controller=cc,
        system_voltage_v=system_voltage_v,
    )
    if not equipment_check["valid"]:
        raise ValueError("Equipment selection is incompatible: " + " | ".join(equipment_check["errors"]))

    result = run_ui_professional_design(
        appliance_records=appliance_records,
        daily_energy_kwh=daily_energy_kwh,
        peak_sun_hours=peak_sun_hours,
        system_voltage_v=system_voltage_v,
        system_derating=system_derating,
        battery_autonomy_days=battery_autonomy_days,
        battery_dod=min(battery_dod, batt.recommended_dod),
        battery_efficiency=min(battery_efficiency, batt.round_trip_efficiency),
        temperature_c=temperature_c,
        panel_rating_w=pv.power_w,
        include_generator=include_generator,
        project_name=project_name,
    )

    pv_capacity_kwp = float(result["pv"]["pv_capacity_kwp"])
    string_design = size_pv_strings(
        pv_capacity_kwp=pv_capacity_kwp,
        module_rating_w=pv.power_w,
        voc_v=pv.voc_v,
        vmp_v=pv.vmp_v,
        isc_a=pv.isc_a,
        imp_a=pv.imp_a,
        controller_max_pv_voltage_v=cc.max_pv_voltage_v if cc else inv.mppt_voltage_max_v,
        controller_min_mppt_voltage_v=cc.min_mppt_voltage_v if cc else inv.mppt_voltage_min_v,
    )
    result["equipment"] = equipment_check["equipment"]
    result["equipment_validation"] = equipment_check
    result["pv"]["string_configuration"] = string_design
    result["design_version"] = "3.0-stage3b"
    return result
