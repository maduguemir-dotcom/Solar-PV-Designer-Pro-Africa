"""Adapters between Product Library records and engineering equipment specs."""
from __future__ import annotations
from typing import Any, Mapping

from .schemas import PVModuleSpec, BatterySpec, InverterSpec, ChargeControllerSpec


def _spec(p: Mapping[str, Any], key: str, default: Any = None) -> Any:
    nested = p.get("specifications")
    if isinstance(nested, Mapping) and key in nested:
        return nested[key]
    return p.get(key, default)


def _num(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _required_number(p: Mapping[str, Any], key: str, label: str, errors: list[str]) -> float:
    value = _num(_spec(p, key))
    if value is None or value <= 0:
        errors.append(f"{label} is missing or not greater than zero.")
        return 1.0
    return value


def _identity(p: Mapping[str, Any]) -> dict[str, str]:
    return {
        "product_id": str(p.get("id", "")),
        "name": str(p.get("name", "")),
        "manufacturer": str(p.get("manufacturer", "") or "Generic"),
        "model": str(p.get("model", "") or p.get("name", "Library Product")),
        "technology": str(p.get("technology", "")),
    }


def adapt_pv_module(product: Mapping[str, Any]) -> tuple[PVModuleSpec | None, dict[str, Any]]:
    errors: list[str] = []
    power = _required_number(product, "rated_power_w", "Rated power", errors)
    voc = _required_number(product, "voc_v", "Voc", errors)
    vmp = _required_number(product, "vmp_v", "Vmp", errors)
    isc = _required_number(product, "isc_a", "Isc", errors)
    imp = _required_number(product, "imp_a", "Imp", errors)
    if errors:
        return None, {"valid": False, "errors": errors, "product": _identity(product)}
    try:
        spec = PVModuleSpec(
            manufacturer=_identity(product)["manufacturer"], model=_identity(product)["model"],
            power_w=power, voc_v=voc, vmp_v=vmp, isc_a=isc, imp_a=imp,
            temp_coeff_voc_pct_per_c=_num(_spec(product, "temperature_coefficient_voc"), -0.29) or -0.29,
            temp_coeff_pmax_pct_per_c=_num(_spec(product, "temperature_coefficient_pmax"), -0.35) or -0.35,
        )
        return spec, {"valid": True, "errors": [], "product": _identity(product)}
    except ValueError as exc:
        return None, {"valid": False, "errors": [str(exc)], "product": _identity(product)}


def adapt_battery(product: Mapping[str, Any]) -> tuple[BatterySpec | None, dict[str, Any]]:
    errors: list[str] = []
    voltage = _num(_spec(product, "nominal_voltage_v")) or _num(product.get("voltage_v"))
    if not voltage or voltage <= 0: errors.append("Nominal voltage is missing or not greater than zero.")
    capacity = _required_number(product, "capacity_ah", "Capacity", errors)
    max_charge = _required_number(product, "max_charge_current_a", "Maximum charge current", errors)
    dod_pct = _num(_spec(product, "depth_of_discharge_percent"))
    eff_pct = _num(_spec(product, "round_trip_efficiency_percent"))
    if dod_pct is None or not 0 < dod_pct <= 100: errors.append("Depth of discharge must be provided as a percentage between 0 and 100.")
    if eff_pct is None or not 0 < eff_pct <= 100: errors.append("Round-trip efficiency must be provided as a percentage between 0 and 100.")
    if errors: return None, {"valid": False, "errors": errors, "product": _identity(product)}
    try:
        spec = BatterySpec(
            manufacturer=_identity(product)["manufacturer"], model=_identity(product)["model"],
            technology=_identity(product)["technology"] or "Battery", nominal_voltage_v=voltage,
            capacity_ah=capacity, recommended_max_continuous_current_a=max_charge,
            recommended_dod=dod_pct/100.0, round_trip_efficiency=eff_pct/100.0,
        )
        return spec, {"valid": True, "errors": [], "product": _identity(product)}
    except ValueError as exc:
        return None, {"valid": False, "errors": [str(exc)], "product": _identity(product)}


def adapt_inverter(product: Mapping[str, Any]) -> tuple[InverterSpec | None, dict[str, Any]]:
    errors: list[str] = []
    continuous = _num(_spec(product, "continuous_power_w")) or _num(product.get("rated_power_w"))
    surge = _required_number(product, "surge_power_w", "Surge power", errors)
    dc_min = _required_number(product, "dc_nominal_voltage_v", "DC nominal voltage", errors)
    dc_max = _required_number(product, "dc_max_voltage_v", "Maximum DC voltage", errors)
    mppt_min = _required_number(product, "mppt_min_voltage_v", "MPPT minimum voltage", errors)
    mppt_max = _required_number(product, "mppt_max_voltage_v", "MPPT maximum voltage", errors)
    pv_power = _required_number(product, "max_pv_input_power_w", "Maximum PV input power", errors)
    max_current = _num(_spec(product, "max_pv_input_current_a"), 18.0) or 18.0
    if not continuous or continuous <= 0: errors.append("Continuous/rated output power is missing or not greater than zero.")
    if errors: return None, {"valid": False, "errors": errors, "product": _identity(product)}
    try:
        spec = InverterSpec(
            manufacturer=_identity(product)["manufacturer"], model=_identity(product)["model"],
            continuous_power_w=continuous, surge_power_w=surge, dc_voltage_min_v=dc_min,
            dc_voltage_max_v=dc_max, mppt_voltage_min_v=mppt_min, mppt_voltage_max_v=mppt_max,
            max_pv_current_a=max_current, max_pv_power_w=pv_power,
        )
        return spec, {"valid": True, "errors": [], "product": _identity(product)}
    except ValueError as exc:
        return None, {"valid": False, "errors": [str(exc)], "product": _identity(product)}


def _system_voltage(value: Any) -> float | None:
    if value is None: return None
    text = str(value).strip().replace("V", "").strip()
    try: return float(text.split("/")[0]) if "/" not in text else None
    except ValueError: return None


def adapt_charge_controller(product: Mapping[str, Any]) -> tuple[ChargeControllerSpec | None, dict[str, Any]]:
    errors: list[str] = []
    system_v = _system_voltage(_spec(product, "system_voltage_v"))
    current = _required_number(product, "max_charge_current_a", "Maximum charge current", errors)
    pv_power = _required_number(product, "max_pv_input_power_w", "Maximum PV input power", errors)
    pv_voltage = _required_number(product, "max_pv_voltage_v", "Maximum PV voltage", errors)
    if system_v is None: errors.append("A single nominal system voltage is required for engineering selection.")
    # Product schema does not currently expose minimum MPPT voltage; keep this explicit rather than inventing it.
    min_mppt = _num(_spec(product, "min_mppt_voltage_v"))
    if min_mppt is None or min_mppt <= 0: errors.append("Minimum MPPT voltage is missing from the product record.")
    if errors: return None, {"valid": False, "errors": errors, "product": _identity(product)}
    try:
        spec = ChargeControllerSpec(
            manufacturer=_identity(product)["manufacturer"], model=_identity(product)["model"],
            battery_voltage_v=system_v, max_pv_voltage_v=pv_voltage, min_mppt_voltage_v=min_mppt,
            max_charge_current_a=current, max_pv_power_w=pv_power,
        )
        return spec, {"valid": True, "errors": [], "product": _identity(product)}
    except ValueError as exc:
        return None, {"valid": False, "errors": [str(exc)], "product": _identity(product)}


ADAPTERS = {
    "Solar Panel": adapt_pv_module,
    "Battery": adapt_battery,
    "Inverter": adapt_inverter,
    "Charge Controller": adapt_charge_controller,
}


def adapt_product(product: Mapping[str, Any]) -> tuple[Any | None, dict[str, Any]]:
    category = str(product.get("category", ""))
    adapter = ADAPTERS.get(category)
    if adapter is None:
        return None, {"valid": False, "errors": [f"Category '{category}' is not engineering-selectable."], "product": _identity(product)}
    return adapter(product)
