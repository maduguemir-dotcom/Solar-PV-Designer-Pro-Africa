from app.ui.equipment_selection import completeness
from app.services.professional_design_service import build_engineering_loads


def test_selector_completeness_valid_record():
    pct, missing = completeness({"validation": {"valid": True}, "product": {"category": "Battery"}})
    assert (pct, missing) == (100, 0)


def test_manual_fallback_remains_available():
    loads = build_engineering_loads([], 5.0)
    assert len(loads) == 1
    assert loads[0].hours_per_day == 5.0
