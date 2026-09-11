from app.services.professional_design_service import build_engineering_loads, run_ui_professional_design


def test_build_loads_from_appliances():
    loads = build_engineering_loads([
        {"name": "Lamp", "power_w": 10, "quantity": 2, "hours_per_day": 5}
    ], 5.0)
    assert len(loads) == 1
    assert loads[0].power_w == 10
    assert loads[0].quantity == 2


def test_manual_energy_fallback():
    loads = build_engineering_loads([], 5.0)
    assert len(loads) == 1
    assert round(loads[0].power_w * loads[0].hours_per_day / 1000, 3) == 5.0


def test_ui_professional_design_returns_validation():
    result = run_ui_professional_design(
        appliance_records=[], daily_energy_kwh=5.0, peak_sun_hours=4.5,
        system_voltage_v=48, system_derating=0.8,
        battery_autonomy_days=2, battery_dod=0.8,
        battery_efficiency=0.9,
    )
    assert result["design_version"] == "3.0-stage2c"
    assert "validation" in result
    assert 0 <= result["design_quality_score"] <= 100
