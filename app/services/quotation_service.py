"""Stage 6B costing and quotation service.

Calculates project costs from explicit line items. Currency conversion is
transparent: every non-quote-currency line requires a user-supplied FX rate.
No market prices are invented by this service.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


def money(value: float | int | Decimal) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class CostLine:
    category: str
    description: str
    quantity: float
    unit_price: float
    currency: str = "USD"
    fx_rate: float = 1.0
    unit: str = "unit"

    def validate(self, quote_currency: str) -> None:
        if not self.description.strip():
            raise ValueError("Line description is required")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        if not self.currency.strip():
            raise ValueError("Currency is required")
        if self.currency.upper() != quote_currency.upper() and self.fx_rate <= 0:
            raise ValueError("A positive FX rate is required for a different currency")
        if self.currency.upper() == quote_currency.upper() and self.fx_rate <= 0:
            raise ValueError("FX rate must be positive")

    def total_quote_currency(self, quote_currency: str) -> float:
        self.validate(quote_currency)
        return money(self.quantity * self.unit_price * self.fx_rate)

    def to_dict(self, quote_currency: str) -> dict:
        data = asdict(self)
        data["currency"] = self.currency.upper()
        data["total"] = self.total_quote_currency(quote_currency)
        return data


def calculate_quote(lines: Iterable[CostLine], *, quote_currency: str = "USD",
                    overhead_percent: float = 0.0, markup_percent: float = 0.0,
                    tax_percent: float = 0.0, contingency_percent: float = 0.0) -> dict:
    currency = quote_currency.strip().upper()
    if not currency:
        raise ValueError("Quote currency is required")
    percentages = {
        "overhead_percent": overhead_percent,
        "markup_percent": markup_percent,
        "tax_percent": tax_percent,
        "contingency_percent": contingency_percent,
    }
    for name, value in percentages.items():
        if value < 0:
            raise ValueError(f"{name} cannot be negative")

    normalized = list(lines)
    line_values = [line.to_dict(currency) for line in normalized]
    direct_cost = money(sum(item["total"] for item in line_values))
    overhead = money(direct_cost * overhead_percent / 100)
    cost_with_overhead = money(direct_cost + overhead)
    contingency = money(cost_with_overhead * contingency_percent / 100)
    cost_base = money(cost_with_overhead + contingency)
    markup = money(cost_base * markup_percent / 100)
    subtotal = money(cost_base + markup)
    tax = money(subtotal * tax_percent / 100)
    grand_total = money(subtotal + tax)
    return {
        "quote_currency": currency,
        "lines": line_values,
        "direct_cost": direct_cost,
        "overhead": overhead,
        "contingency": contingency,
        "cost_base": cost_base,
        "markup": markup,
        "subtotal": subtotal,
        "tax": tax,
        "grand_total": grand_total,
        "gross_margin_value": markup,
        "gross_margin_percent_of_sale": money(markup / grand_total * 100) if grand_total else 0.0,
        **percentages,
    }
