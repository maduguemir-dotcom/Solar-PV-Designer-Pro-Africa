"""Bridge the central Product Library to professional engineering selection."""
from __future__ import annotations
from typing import Any

try:
    from product_engine import get_products, get_product
    from equipment.product_adapter import adapt_product
    from equipment.selection import validate_equipment_selection
except ModuleNotFoundError:
    from app.product_engine import get_products, get_product
    from app.equipment.product_adapter import adapt_product
    from app.equipment.selection import validate_equipment_selection


def engineering_library_products(category: str) -> list[dict[str, Any]]:
    """Return library records that are structurally ready for engineering use."""
    results = []
    for product in get_products():
        if str(product.get("category", "")) != category:
            continue
        spec, check = adapt_product(product)
        results.append({"product": product, "spec": spec, "validation": check})
    return results


def get_engineering_product(product_id: str) -> dict[str, Any] | None:
    product = get_product(product_id)
    if not product:
        return None
    spec, validation = adapt_product(product)
    return {"product": product, "spec": spec, "validation": validation}


def select_engineering_equipment(*, pv_product_id: str, battery_product_id: str,
                                  inverter_product_id: str, charge_controller_product_id: str | None = None,
                                  system_voltage_v: float = 48.0) -> dict[str, Any]:
    selected = {}
    errors: list[str] = []
    warnings: list[str] = []
    ids = {"pv_module": pv_product_id, "battery": battery_product_id, "inverter": inverter_product_id}
    if charge_controller_product_id:
        ids["charge_controller"] = charge_controller_product_id
    for role, pid in ids.items():
        item = get_engineering_product(pid)
        if not item:
            errors.append(f"Product '{pid}' could not be found in the central Product Library.")
            continue
        selected[role] = item
        errors.extend([f"{role}: {e}" for e in item["validation"]["errors"]])
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "selected": selected}
    pv = selected["pv_module"]["spec"]
    batt = selected["battery"]["spec"]
    inv = selected["inverter"]["spec"]
    cc = selected.get("charge_controller", {}).get("spec") if "charge_controller" in selected else None
    compatibility = validate_equipment_selection(pv_module=pv, battery=batt, inverter=inv,
                                                  charge_controller=cc, system_voltage_v=system_voltage_v)
    return {"valid": compatibility["valid"], "errors": compatibility["errors"],
            "warnings": compatibility["warnings"], "selected": selected,
            "compatibility": compatibility}
