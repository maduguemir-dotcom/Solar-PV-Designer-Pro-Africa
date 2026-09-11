from app.engineering.battery_electrical import configure_battery_bank, check_battery_inverter_compatibility
from app.engineering.generator_sizing import size_generator
from app.engineering.system_architecture import build_system_architecture
from app.engineering.design_engine_v3 import run_professional_design


def test_battery_configuration():
    r = configure_battery_bank(nominal_battery_ah=500, system_voltage_v=48, unit_voltage_v=12, unit_capacity_ah=200, max_continuous_current_a=100)
    assert r["series_units"] == 4
    assert r["parallel_strings"] == 3
    assert r["total_battery_units"] == 12


def test_generator_sizing():
    r = size_generator(peak_load_w=4000, battery_charging_power_w=1000)
    assert r["recommended_generator_kva"] >= r["required_generator_kva"]


def test_compatibility():
    assert check_battery_inverter_compatibility(battery_voltage_v=48)["compatible"]


def test_architecture():
    r = build_system_architecture(system_voltage_v=48, ac_voltage_v=230, include_generator=True)
    assert r["generator_path"] is not None


def test_professional_design():
    loads = [{"name": "Load", "quantity": 1, "power_w": 1000, "hours_per_day": 5}]
    r = run_professional_design(loads, peak_sun_hours=5, battery_unit_voltage_v=12, battery_unit_capacity_ah=200, include_generator=True)
    assert r["design_version"] == "3.0-stage2c"
    assert r["pv"]["panel_count"] > 0
    assert r["electrical"]["pv_strings"]["series_modules"] > 0
