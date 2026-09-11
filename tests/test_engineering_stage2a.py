from app.engineering.load_analysis import LoadItem, analyze_loads
from app.engineering.pv_sizing import size_pv_array, panel_count
from app.engineering.battery_sizing import size_battery_bank
from app.engineering.inverter_sizing import size_inverter
from app.engineering.design_engine import run_engineering_design


def test_load_analysis():
    result = analyze_loads([
        LoadItem("Lamp", 10, 10, 5),
        LoadItem("TV", 1, 100, 5),
    ])
    assert result["total_connected_load_w"] == 200
    assert result["daily_energy_kwh"] == 1.0


def test_pv_sizing():
    result = size_pv_array(5, 4, system_derating=0.8, design_margin=1.1)
    assert round(result["pv_capacity_kwp"], 3) == round(5 / (4 * 0.8) * 1.1, 3)
    assert panel_count(result["pv_capacity_kwp"], 550) >= 1


def test_battery_sizing():
    result = size_battery_bank(5, 2, 48, depth_of_discharge=0.8, battery_efficiency=0.9)
    assert result["nominal_battery_kwh"] > 10
    assert result["nominal_battery_ah"] > 200


def test_inverter_sizing_uses_load():
    result = size_inverter(3000, 6000, design_margin=1.25)
    assert result["recommended_continuous_w"] == 3750
    assert result["recommended_surge_w"] == 7500


def test_full_stage2a_engine():
    result = run_engineering_design(
        [
            {"name": "Lighting", "quantity": 10, "power_w": 10, "hours_per_day": 5},
            {"name": "TV", "quantity": 1, "power_w": 100, "hours_per_day": 5},
        ],
        peak_sun_hours=4,
    )
    assert result["load"]["daily_energy_kwh"] == 1.0
    assert result["pv"]["pv_capacity_kwp"] > 0
    assert result["battery"]["nominal_battery_kwh"] > 0
    assert result["inverter"]["recommended_continuous_w"] > 0
