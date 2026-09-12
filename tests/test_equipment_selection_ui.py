from app.ui.equipment_selection import completeness


def test_valid_product_is_fully_complete():
    pct, missing = completeness({"validation": {"valid": True}, "product": {"category": "Solar Panel"}})
    assert pct == 100
    assert missing == 0


def test_incomplete_pv_product_reports_missing_fields():
    item = {"validation": {"valid": False, "errors": ["Voc missing"]}, "product": {
        "category": "Solar Panel", "rated_power_w": 550,
        "specifications": {"voc_v": 0, "vmp_v": 41.5, "isc_a": 14, "imp_a": 13.3}
    }}
    pct, missing = completeness(item)
    assert pct == 80
    assert missing == 1
