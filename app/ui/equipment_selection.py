"""Engineering-ready Product Library selection UI.

The UI reads from the central Product Library through the Stage 3C service;
it does not create a second product database.
"""
from __future__ import annotations
from typing import Any


def _label(item: dict[str, Any]) -> str:
    p = item.get("product", {})
    name = str(p.get("name", "Unnamed product"))
    manufacturer = str(p.get("manufacturer", "") or "")
    model = str(p.get("model", "") or "")
    identity = " ".join(x for x in (manufacturer, model) if x)
    return f"{name} — {identity}" if identity else name


def engineering_catalog(category: str) -> list[dict[str, Any]]:
    try:
        from services.product_library_engine import engineering_library_products
    except ModuleNotFoundError:
        from app.services.product_library_engine import engineering_library_products
    return engineering_library_products(category)


def completeness(item: dict[str, Any]) -> tuple[int, int]:
    validation = item.get("validation", {})
    errors = validation.get("errors", [])
    # Valid adapters represent a complete engineering record. For invalid
    # records we report a conservative completeness estimate from required fields.
    if validation.get("valid"):
        return 100, 0
    product = item.get("product", {})
    category = product.get("category")
    required = {
        "Solar Panel": ["rated_power_w", "voc_v", "vmp_v", "isc_a", "imp_a"],
        "Battery": ["nominal_voltage_v", "capacity_ah", "max_charge_current_a",
                     "depth_of_discharge_percent", "round_trip_efficiency_percent"],
        "Inverter": ["rated_power_w", "surge_power_w", "dc_nominal_voltage_v",
                      "dc_max_voltage_v", "mppt_min_voltage_v", "mppt_max_voltage_v",
                      "max_pv_input_power_w"],
        "Charge Controller": ["system_voltage_v", "max_charge_current_a",
                               "max_pv_input_power_w", "max_pv_voltage_v", "min_mppt_voltage_v"],
    }.get(category, [])
    nested = product.get("specifications") if isinstance(product.get("specifications"), dict) else {}
    present = sum(1 for key in required if product.get(key) not in (None, "", 0) or nested.get(key) not in (None, "", 0))
    return (round(100 * present / len(required)) if required else 0), max(0, len(required) - present)


def render_engineering_equipment_selector(st, system_voltage_v: float = 48.0) -> dict[str, Any] | None:
    """Render selector and return selected engineering products/specs.

    Returns None when selection is incomplete or the user has not clicked
    the confirmation button. Selection is stored by the caller if desired.
    """
    try:
        from services.product_library_engine import select_engineering_equipment
    except ModuleNotFoundError:
        from app.services.product_library_engine import select_engineering_equipment

    st.subheader("🧰 Select Engineering Equipment")
    st.caption("Select equipment from the central Product Library. Only records with sufficient technical data should be used for professional design.")

    categories = [
        ("pv_module", "Solar Panel", "PV Module"),
        ("battery", "Battery", "Battery"),
        ("inverter", "Inverter", "Inverter"),
        ("charge_controller", "Charge Controller", "Charge Controller (optional)"),
    ]
    catalogs = {key: engineering_catalog(category) for key, category, _ in categories}

    selected_ids: dict[str, str | None] = {}
    for key, category, title in categories:
        items = catalogs[key]
        if not items:
            st.info(f"No {category} records are currently available in the Product Library.")
            selected_ids[key] = None
            continue
        labels = [_label(item) for item in items]
        options = [None] + list(range(len(items))) if key == "charge_controller" else list(range(len(items)))
        choice = st.selectbox(
            title,
            options,
            format_func=lambda x, labels=labels: "— None —" if x is None else labels[x],
            key=f"engineering_equipment_{key}",
        )
        selected_ids[key] = None if choice is None else str(items[choice]["product"].get("id", ""))
        if choice is not None:
            item = items[choice]
            pct, missing = completeness(item)
            if item.get("validation", {}).get("valid"):
                st.success(f"Engineering data: {pct}% complete — ready for selection")
            else:
                st.warning(f"Engineering data: approximately {pct}% complete — {missing} required field(s) missing")
                for err in item.get("validation", {}).get("errors", []):
                    st.caption(f"• {err}")

    if not selected_ids.get("pv_module") or not selected_ids.get("battery") or not selected_ids.get("inverter"):
        st.warning("Select a PV module, battery and inverter to enable professional equipment validation.")
        return None

    if st.button("✅ Validate & Use Selected Equipment", key="validate_engineering_equipment", use_container_width=True):
        result = select_engineering_equipment(
            pv_product_id=selected_ids["pv_module"],
            battery_product_id=selected_ids["battery"],
            inverter_product_id=selected_ids["inverter"],
            charge_controller_product_id=selected_ids.get("charge_controller"),
            system_voltage_v=float(system_voltage_v),
        )
        return result
    return None
