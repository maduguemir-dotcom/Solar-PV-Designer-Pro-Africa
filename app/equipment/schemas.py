"""Typed equipment specifications used by the professional design workflow."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


def _positive(name: str, value: float) -> float:
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value

@dataclass(frozen=True)
class PVModuleSpec:
    manufacturer: str = "Generic"
    model: str = "550 W Module"
    power_w: float = 550.0
    voc_v: float = 49.5
    vmp_v: float = 41.5
    isc_a: float = 14.0
    imp_a: float = 13.3
    temp_coeff_voc_pct_per_c: float = -0.29
    temp_coeff_pmax_pct_per_c: float = -0.35

    def __post_init__(self):
        for name in ("power_w", "voc_v", "vmp_v", "isc_a", "imp_a"):
            _positive(name, getattr(self, name))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class BatterySpec:
    manufacturer: str = "Generic"
    model: str = "48 V Lithium Battery"
    technology: str = "Lithium"
    nominal_voltage_v: float = 48.0
    capacity_ah: float = 100.0
    recommended_max_continuous_current_a: float = 100.0
    recommended_dod: float = 0.80
    round_trip_efficiency: float = 0.90

    def __post_init__(self):
        _positive("nominal_voltage_v", self.nominal_voltage_v)
        _positive("capacity_ah", self.capacity_ah)
        _positive("recommended_max_continuous_current_a", self.recommended_max_continuous_current_a)
        if not 0 < self.recommended_dod <= 1:
            raise ValueError("recommended_dod must be > 0 and <= 1.")
        if not 0 < self.round_trip_efficiency <= 1:
            raise ValueError("round_trip_efficiency must be > 0 and <= 1.")

    @property
    def nominal_energy_kwh(self) -> float:
        return self.nominal_voltage_v * self.capacity_ah / 1000.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"nominal_energy_kwh": self.nominal_energy_kwh}

@dataclass(frozen=True)
class InverterSpec:
    manufacturer: str = "Generic"
    model: str = "5 kW Hybrid Inverter"
    continuous_power_w: float = 5000.0
    surge_power_w: float = 10000.0
    dc_voltage_min_v: float = 40.0
    dc_voltage_max_v: float = 60.0
    mppt_voltage_min_v: float = 60.0
    mppt_voltage_max_v: float = 450.0
    max_pv_current_a: float = 18.0
    max_pv_power_w: float = 6500.0

    def __post_init__(self):
        for name in ("continuous_power_w", "surge_power_w", "dc_voltage_min_v", "dc_voltage_max_v", "mppt_voltage_min_v", "mppt_voltage_max_v", "max_pv_current_a", "max_pv_power_w"):
            _positive(name, getattr(self, name))
        if self.surge_power_w < self.continuous_power_w:
            raise ValueError("surge_power_w must be >= continuous_power_w.")
        if self.dc_voltage_max_v <= self.dc_voltage_min_v or self.mppt_voltage_max_v <= self.mppt_voltage_min_v:
            raise ValueError("Voltage maximums must exceed minimums.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ChargeControllerSpec:
    manufacturer: str = "Generic"
    model: str = "150 V / 60 A MPPT"
    battery_voltage_v: float = 48.0
    max_pv_voltage_v: float = 150.0
    min_mppt_voltage_v: float = 60.0
    max_charge_current_a: float = 60.0
    max_pv_power_w: float = 3000.0

    def __post_init__(self):
        for name in ("battery_voltage_v", "max_pv_voltage_v", "min_mppt_voltage_v", "max_charge_current_a", "max_pv_power_w"):
            _positive(name, getattr(self, name))
        if self.max_pv_voltage_v <= self.min_mppt_voltage_v:
            raise ValueError("max_pv_voltage_v must exceed min_mppt_voltage_v.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class CableSpec:
    material: str = "Copper"
    cross_section_mm2: float = 6.0
    length_m: float = 20.0
    resistance_ohm_per_km: float = 3.08
    voltage_system_v: float = 48.0

    def __post_init__(self):
        for name in ("cross_section_mm2", "length_m", "resistance_ohm_per_km", "voltage_system_v"):
            _positive(name, getattr(self, name))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
