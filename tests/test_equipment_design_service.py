from app.equipment.schemas import PVModuleSpec, BatterySpec, InverterSpec, ChargeControllerSpec
from app.equipment.selection import validate_equipment_selection
from app.services.equipment_design_service import run_equipment_aware_design


def test_equipment_defaults_are_valid():
    check = validate_equipment_selection(
        pv_module=PVModuleSpec(), battery=BatterySpec(), inverter=InverterSpec(),
        charge_controller=ChargeControllerSpec(), system_voltage_v=48,
    )
    assert check["valid"]


def test_voltage_mismatch_is_rejected():
    check = validate_equipment_selection(
        pv_module=PVModuleSpec(), battery=BatterySpec(nominal_voltage_v=24),
        inverter=InverterSpec(), charge_controller=ChargeControllerSpec(), system_voltage_v=48,
    )
    assert not check["valid"]
    assert check["errors"]


def test_equipment_aware_design():
    result = run_equipment_aware_design(
        appliance_records=[], daily_energy_kwh=5.0, peak_sun_hours=4.5,
        system_voltage_v=48, system_derating=0.8,
        battery_autonomy_days=2, battery_dod=0.8, battery_efficiency=0.9,
    )
    assert result["design_version"] == "3.0-stage3b"
    assert "equipment" in result
    assert "string_configuration" in result["pv"]
