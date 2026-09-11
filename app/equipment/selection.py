"""Equipment compatibility checks before a professional design is accepted."""
from __future__ import annotations
from typing import Any
from .schemas import PVModuleSpec, BatterySpec, InverterSpec, ChargeControllerSpec


def validate_equipment_selection(
    *,
    pv_module: PVModuleSpec,
    battery: BatterySpec,
    inverter: InverterSpec,
    charge_controller: ChargeControllerSpec | None = None,
    system_voltage_v: float = 48.0,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if abs(battery.nominal_voltage_v - system_voltage_v) > 1e-9:
        errors.append(f"Battery nominal voltage ({battery.nominal_voltage_v:g} V) does not match system voltage ({system_voltage_v:g} V).")

    if battery.nominal_voltage_v < inverter.dc_voltage_min_v or battery.nominal_voltage_v > inverter.dc_voltage_max_v:
        errors.append("Selected battery voltage is outside the inverter DC battery-voltage range.")

    if pv_module.imp_a > inverter.max_pv_current_a:
        warnings.append("A single PV module Imp exceeds the inverter's stated maximum PV input current; verify string/current architecture and manufacturer limits.")

    if pv_module.vmp_v >= inverter.mppt_voltage_max_v:
        errors.append("PV module Vmp is already at or above the inverter MPPT maximum; string design cannot correct this safely.")

    if charge_controller:
        if abs(charge_controller.battery_voltage_v - system_voltage_v) > 1e-9:
            errors.append("Charge-controller battery voltage does not match the selected system voltage.")
        if pv_module.voc_v >= charge_controller.max_pv_voltage_v:
            errors.append("A single module Voc is at or above the charge controller's maximum PV voltage.")
        if pv_module.vmp_v < charge_controller.min_mppt_voltage_v:
            warnings.append("A single module Vmp is below the controller's minimum MPPT voltage; use an appropriate series string.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "equipment": {
            "pv_module": pv_module.to_dict(),
            "battery": battery.to_dict(),
            "inverter": inverter.to_dict(),
            "charge_controller": charge_controller.to_dict() if charge_controller else None,
        },
    }
