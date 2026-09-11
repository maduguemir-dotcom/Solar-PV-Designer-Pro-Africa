"""Stage 2D professional design wrapper with validation intelligence."""
from __future__ import annotations
from typing import Any
from .design_engine_v3 import run_professional_design
from .design_intelligence import validate_professional_design, build_assumptions_register


def run_validated_professional_design(*args, **kwargs) -> dict[str, Any]:
    """Run Stage 2C design, then attach validation, score and assumptions."""
    design = run_professional_design(*args, **kwargs)
    validation = validate_professional_design(design)
    design["validation"] = validation
    design["design_quality_score"] = validation["score"]
    design["design_status"] = validation["status"]
    design["assumptions_register"] = build_assumptions_register(
        system_voltage_v=kwargs.get("system_voltage_v", 48.0),
        ac_voltage_v=kwargs.get("ac_voltage_v", 230.0),
        peak_sun_hours=kwargs.get("peak_sun_hours", 0.0),
        system_derating=kwargs.get("system_derating", 0.80),
        design_margin=kwargs.get("design_margin", 1.10),
        battery_dod=kwargs.get("battery_dod", 0.80),
        battery_efficiency=kwargs.get("battery_efficiency", 0.90),
    )
    return design
