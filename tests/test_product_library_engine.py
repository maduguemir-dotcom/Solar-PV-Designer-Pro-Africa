from app.equipment.product_adapter import adapt_pv_module, adapt_battery, adapt_inverter, adapt_charge_controller


def test_pv_adapter_from_product_record():
    spec, result = adapt_pv_module({"id": "pv1", "name": "Test 550W", "category": "Solar Panel",
        "manufacturer": "TestCo", "model": "T550", "rated_power_w": 550,
        "specifications": {"voc_v": 49.5, "vmp_v": 41.5, "isc_a": 14, "imp_a": 13.3,
                           "temperature_coefficient_voc": -0.29, "temperature_coefficient_pmax": -0.35}})
    assert result["valid"] is True
    assert spec.power_w == 550
    assert spec.voc_v == 49.5


def test_battery_adapter_converts_percentages():
    spec, result = adapt_battery({"id": "b1", "name": "48V 100Ah", "category": "Battery",
        "manufacturer": "TestCo", "technology": "Lithium", "specifications": {
            "nominal_voltage_v": 48, "capacity_ah": 100, "max_charge_current_a": 100,
            "depth_of_discharge_percent": 80, "round_trip_efficiency_percent": 90}})
    assert result["valid"] is True
    assert spec.recommended_dod == 0.8
    assert spec.round_trip_efficiency == 0.9


def test_inverter_adapter():
    spec, result = adapt_inverter({"id": "i1", "name": "5kW", "category": "Inverter", "manufacturer": "TestCo",
        "rated_power_w": 5000, "specifications": {"continuous_power_w": 5000, "surge_power_w": 10000,
        "dc_nominal_voltage_v": 48, "dc_max_voltage_v": 60, "mppt_min_voltage_v": 60,
        "mppt_max_voltage_v": 450, "max_pv_input_power_w": 6500}})
    assert result["valid"] is True
    assert spec.continuous_power_w == 5000


def test_controller_requires_explicit_min_mppt():
    _, result = adapt_charge_controller({"id": "cc1", "name": "60A", "category": "Charge Controller",
        "specifications": {"system_voltage_v": "48 V", "max_charge_current_a": 60,
        "max_pv_input_power_w": 3000, "max_pv_voltage_v": 150}})
    assert result["valid"] is False
    assert any("Minimum MPPT voltage" in e for e in result["errors"])
