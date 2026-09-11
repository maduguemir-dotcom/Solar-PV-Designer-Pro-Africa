# Stage 2B — Professional Electrical Engineering Engine

## Purpose

Stage 2B extends the Stage 2A engineering foundation with an electrical-design layer for PV strings, MPPT charge controllers, cables and protection architecture.

## Added modules

- `app/engineering/pv_electrical.py` — module/string sizing using cold Voc and hot Vmp checks.
- `app/engineering/charge_controller.py` — indicative MPPT current sizing and PV-voltage compatibility check.
- `app/engineering/cable_sizing.py` — DC/single-phase AC voltage-drop calculation with standard conductor-size selection.
- `app/engineering/protection.py` — indicative PV overcurrent and AC breaker sizing plus protection architecture checklist.
- `app/engineering/electrical_design.py` — Stage 2B orchestration layer.
- `app/engineering/stage2b_validation.py` — non-fatal validation/warning layer.
- `tests/test_engineering_stage2b.py` — automated Stage 2B calculation tests.

## Engineering assumptions

The calculations are intentionally transparent and conservative, but they are **not a substitute for final engineering approval**. Final selection must use the exact equipment datasheets and applicable national/local electrical standards.

In particular, verify:

1. Module Voc/Vmp/Isc/Imp and temperature coefficients.
2. MPPT minimum/maximum operating voltage and maximum PV input current.
3. Controller battery-current and thermal limits.
4. Cable ampacity, conductor material, insulation, installation method, ambient temperature and grouping.
5. Fuse/breaker breaking capacity and manufacturer maximum-series-fuse requirements.
6. DC/AC isolators, SPDs, earthing/bonding and RCD/RCBO requirements according to the applicable code.

## Migration policy

Stage 2B does **not** modify `app/main.py`. The existing Streamlit UI remains unchanged until Stage 2 engineering modules have been validated. UI migration will be handled as a later controlled stage.

## Testing

Run:

```text
pytest tests/test_engineering_stage2a.py tests/test_engineering_stage2b.py -q
```

If the environment does not have the application's optional UI dependencies, the pure engineering tests can still be run independently after the Python package dependencies required by the tests are installed.
