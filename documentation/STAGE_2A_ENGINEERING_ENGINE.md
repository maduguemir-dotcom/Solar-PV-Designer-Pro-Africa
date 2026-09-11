# Stage 2A — Professional Engineering Engine Foundation

Stage 2A introduces a pure-Python engineering layer that is independent of
Streamlit UI.

## Modules

- `app/engineering/load_analysis.py`
- `app/engineering/pv_sizing.py`
- `app/engineering/battery_sizing.py`
- `app/engineering/inverter_sizing.py`
- `app/engineering/design_engine.py`
- `app/engineering/engineering_validation.py`

## Engineering basis introduced

### Load
- connected load
- daily energy
- monthly energy
- diversity factor
- peak operating load
- surge-load basis

### PV
- peak sun hours
- system derating
- design margin
- temperature correction
- module count

### Battery
- autonomy
- system voltage
- DoD
- battery efficiency
- design margin
- nominal kWh
- nominal Ah
- optional series/parallel calculation

### Inverter
- peak operating load
- peak surge load
- design margin
- power factor
- continuous and surge VA/kVA

## Deliberate limitation

Stage 2A is a design-basis engine, not yet the complete final PV engineering
suite. It does not yet perform module electrical string design, charge
controller sizing, cable/voltage-drop sizing, protection-device selection,
financial analysis, or equipment-specific validation.

Those are subsequent Stage 2 modules.

## Migration rule

The existing v2.4 calculation modules remain in place. `main.py` is not
switched wholesale to the new engine until the new calculations have been
validated against representative design cases and the UI integration has
been tested.
