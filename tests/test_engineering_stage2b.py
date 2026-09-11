from app.engineering.pv_electrical import size_pv_strings
from app.engineering.charge_controller import size_charge_controller
from app.engineering.cable_sizing import size_cable
from app.engineering.protection import size_pv_overcurrent_protection
from app.engineering.electrical_design import run_electrical_design
from app.engineering.stage2b_validation import validate_electrical_design


def test_pv_string_sizing():
    result = size_pv_strings(
        pv_capacity_kwp=5.5,
        module_rating_w=550,
        voc_v=49.5,
        vmp_v=41.5,
        isc_a=14,
        imp_a=13.3,
        controller_max_pv_voltage_v=450,
        controller_min_mppt_voltage_v=120,
    )
    assert result["series_modules"] >= 3
    assert result["total_modules"] >= result["required_modules"]
    assert result["cold_string_voc_v"] < 450


def test_charge_controller():
    result = size_charge_controller(pv_capacity_kwp=5.5, system_voltage_v=48)
    assert result["design_current_a"] > result["required_current_a"]


def test_cable_sizing():
    result = size_cable(
        current_a=25,
        one_way_length_m=20,
        system_voltage_v=48,
        max_voltage_drop_pct=3,
    )
    assert result["selected_area_mm2"] >= result["required_area_mm2"]
    assert result["actual_voltage_drop_pct"] <= 3


def test_protection():
    result = size_pv_overcurrent_protection(module_isc_a=14, parallel_strings=4)
    assert result["string_fuse_rating_a"] >= 14
    assert result["array_overcurrent_rating_a"] >= result["array_isc_a"]


def test_full_stage2b_design():
    design = run_electrical_design(
        pv_capacity_kwp=5.5,
        module_rating_w=550,
        module_voc_v=49.5,
        module_vmp_v=41.5,
        module_isc_a=14,
        module_imp_a=13.3,
        controller_max_pv_voltage_v=450,
        controller_min_mppt_voltage_v=120,
        system_voltage_v=48,
        peak_operating_load_w=3500,
        pv_cable_length_m=15,
        battery_cable_length_m=3,
        ac_cable_length_m=20,
        battery_current_a=80,
        ac_voltage_v=230,
    )
    validation = validate_electrical_design(design)
    assert "pv_strings" in design
    assert "charge_controller" in design
    assert "cables" in design
    assert "protection" in design
    assert validation["valid"]
