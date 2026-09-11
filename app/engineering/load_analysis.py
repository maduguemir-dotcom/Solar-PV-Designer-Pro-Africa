"""Electrical load analysis.

All calculations are unit-explicit and independent of Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class LoadItem:
    """One electrical load/appliance in the design."""

    name: str
    quantity: float
    power_w: float
    hours_per_day: float
    days_per_week: float = 7.0
    surge_factor: float = 1.0
    is_surge_load: bool = False

    def __post_init__(self) -> None:
        if self.quantity < 0 or self.power_w < 0:
            raise ValueError("Quantity and power must be non-negative.")
        if not 0 <= self.hours_per_day <= 24:
            raise ValueError("Hours per day must be between 0 and 24.")
        if not 0 <= self.days_per_week <= 7:
            raise ValueError("Days per week must be between 0 and 7.")
        if self.surge_factor < 1:
            raise ValueError("Surge factor must be at least 1.")


def analyze_loads(
    loads: Iterable[LoadItem | Mapping[str, Any]],
    *,
    diversity_factor: float = 1.0,
) -> dict:
    """Calculate connected load, daily/monthly energy and design demand.

    ``diversity_factor`` represents the fraction of connected load expected
    to operate simultaneously. It is deliberately explicit rather than
    hidden inside another calculation.
    """
    if not 0 < diversity_factor <= 1:
        raise ValueError("Diversity factor must be > 0 and <= 1.")

    normalized = []
    for item in loads:
        load = item if isinstance(item, LoadItem) else LoadItem(
            name=str(item.get("name", item.get("Appliance", "Load"))),
            quantity=float(item.get("quantity", item.get("Quantity", 1))),
            power_w=float(item.get("power_w", item.get("Typical_Wattage", item.get("Power_W", 0)))),
            hours_per_day=float(item.get("hours_per_day", item.get("Hours_Per_Day", 0))),
            days_per_week=float(item.get("days_per_week", item.get("Days_Per_Week", 7))),
            surge_factor=float(item.get("surge_factor", 1.0)),
            is_surge_load=bool(item.get("is_surge_load", False)),
        )
        normalized.append(load)

    connected_w = sum(x.quantity * x.power_w for x in normalized)
    daily_kwh = sum(
        x.quantity * x.power_w * x.hours_per_day * (x.days_per_week / 7.0) / 1000
        for x in normalized
    )
    monthly_kwh = daily_kwh * 365.0 / 12.0

    # Operating demand is based on simultaneous connected load.
    peak_operating_w = connected_w * diversity_factor

    # Conservative surge estimate: only loads marked as surge loads contribute
    # their additional starting demand; non-surge loads remain at rated power.
    base_operating_w = peak_operating_w
    surge_additional_w = sum(
        x.quantity * x.power_w * (x.surge_factor - 1.0)
        for x in normalized
        if x.is_surge_load
    )
    peak_surge_w = base_operating_w + surge_additional_w

    return {
        "items": [asdict(x) for x in normalized],
        "total_connected_load_w": connected_w,
        "daily_energy_kwh": daily_kwh,
        "monthly_energy_kwh": monthly_kwh,
        "diversity_factor": diversity_factor,
        "peak_operating_load_w": peak_operating_w,
        "peak_surge_load_w": peak_surge_w,
    }
