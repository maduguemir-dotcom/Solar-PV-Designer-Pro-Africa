from app.engineering.load_analysis import LoadItem
from app.engineering.design_engine_v4 import run_validated_professional_design
from app.engineering.design_intelligence import validate_professional_design, calculate_design_quality_score


def sample_design():
    loads = [LoadItem("Lights", 10, 10, 5), LoadItem("Fridge", 1, 150, 8, surge_factor=2, is_surge_load=True)]
    return run_validated_professional_design(
        loads, peak_sun_hours=5, system_voltage_v=48, panel_rating_w=550,
        module_voc_v=49.5, module_vmp_v=41.5, module_isc_a=14, module_imp_a=13.3,
        controller_max_pv_voltage_v=150, controller_min_mppt_voltage_v=60,
        battery_unit_voltage_v=12, battery_unit_capacity_ah=200,
        project_name="Stage 2D Test"
    )


def test_validation_attached():
    result = sample_design()
    assert "validation" in result
    assert 0 <= result["design_quality_score"] <= 100
    assert result["assumptions_register"]


def test_quality_score_all_pass():
    checks = [{"passed": True, "severity": "error"}, {"passed": True, "severity": "warning"}]
    assert calculate_design_quality_score(checks) == 100.0


def test_validator_catches_zero_load():
    result = validate_professional_design({"load": {}, "pv": {}, "battery": {}, "inverter": {}, "electrical": {}})
    assert result["errors"]
    assert result["score"] < 100
