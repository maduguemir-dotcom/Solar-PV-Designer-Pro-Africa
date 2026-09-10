"""Stage 1B module registry.

This file records architectural decisions without deleting legacy modules.
The goal is to make future consolidation deliberate and traceable.
"""

AUTHORITATIVE_CURRENT = {
    "design_service": "services.design_service",
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
    "solar_calculator": [
        "solar_calculator",
        "app.app.solar_calculator",
    ],
    "battery": [
        "battery_model",
    ],
    "inverter": [
        "inverter_model",
    ],
    "costing": [
        "cost_estimator",
        "cost_engine",
    ],
    "database": [
        "database",
        "library_store",
    ],
}

# These modules remain in the repository during the transition.
# They must not be deleted until dependency mapping and tests are complete.
DEFERRED_DEPRECATION = (
    "solar_calculator",
    "battery_model",
    "inverter_model",
    "cost_estimator",
    "cost_engine",
    "database",
)


def architecture_summary() -> dict:
    """Return a machine-readable summary for diagnostics and future tooling."""
    return {
        "authoritative_current": dict(AUTHORITATIVE_CURRENT),
        "legacy_or_overlapping": dict(LEGACY_OR_OVERLAPPING),
        "deferred_deprecation": list(DEFERRED_DEPRECATION),
    }
