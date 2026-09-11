"""Central map of authoritative and legacy modules during migration."""

AUTHORITATIVE_CURRENT = {
    "design_service": "services.design_service",
    "engineering_engine": "engineering.design_engine",
    "electrical_engine": "engineering.electrical_design",
    "session_state": "core.session_state",
    "product_storage": "library_store",
    "product_engine": "product_engine",
    "product_ui": "product_ui",
    "cost_diary": "costing",
    "location_search": "location_search",
    "location_engine": "location_engine",
    "solar_analytics": "solar_analytics",
}

LEGACY_OR_OVERLAPPING = {
    "solar_calculator": ["solar_calculator", "app.app.solar_calculator"],
    "battery": ["battery_model"],
    "inverter": ["inverter_model"],
    "costing": ["cost_estimator", "cost_engine"],
    "persistence": ["database", "library_store"],
}
