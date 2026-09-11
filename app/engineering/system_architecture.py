"""Unified high-level DC/AC architecture description."""
from __future__ import annotations


def build_system_architecture(*, system_voltage_v: float, ac_voltage_v: float, include_generator: bool = False) -> dict:
    return {
        "dc_bus": f"{system_voltage_v:.0f} V nominal battery/DC bus",
        "pv_path": "PV array -> DC isolator/overcurrent protection -> MPPT charge controller -> battery bus",
        "battery_path": "Battery bank -> battery fuse/breaker -> DC isolator -> inverter",
        "ac_path": f"Inverter -> AC isolator/breaker -> {ac_voltage_v:.0f} V AC distribution",
        "protection": ["PV DC overcurrent protection", "PV DC isolator", "battery overcurrent protection", "battery DC isolator", "AC main breaker/isolator", "appropriate DC/AC surge protection"],
        "generator_path": "Generator -> approved transfer/changeover arrangement -> AC bus" if include_generator else None,
        "note": "Final topology, ratings, earthing and protection must follow equipment manuals and applicable electrical codes.",
    }
