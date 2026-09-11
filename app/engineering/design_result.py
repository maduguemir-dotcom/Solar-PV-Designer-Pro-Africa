"""Common result envelope for the professional engineering engine."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EngineeringDesignResult:
    project_name: str = "Untitled Project"
    design_version: str = "3.0-stage2c"
    load: dict[str, Any] = field(default_factory=dict)
    pv: dict[str, Any] = field(default_factory=dict)
    battery: dict[str, Any] = field(default_factory=dict)
    inverter: dict[str, Any] = field(default_factory=dict)
    electrical: dict[str, Any] = field(default_factory=dict)
    generator: dict[str, Any] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "design_version": self.design_version,
            "load": self.load,
            "pv": self.pv,
            "battery": self.battery,
            "inverter": self.inverter,
            "electrical": self.electrical,
            "generator": self.generator,
            "architecture": self.architecture,
            "warnings": self.warnings,
            "errors": self.errors,
        }
