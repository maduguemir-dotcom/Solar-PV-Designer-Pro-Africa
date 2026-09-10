# Solar PV Designer Pro Africa™ — Stage 1B Codebase Stabilization

## Purpose

Stage 1B reduces architectural ambiguity without making destructive changes.
The objective is to establish which modules are currently authoritative before
the professional engineering engine is introduced.

## Current authoritative paths

| Area | Current module |
|---|---|
| Design orchestration | `app/services/design_service.py` |
| Session state | `app/core/session_state.py` |
| Product persistence | `app/library_store.py` |
| Product logic | `app/product_engine.py` |
| Product UI | `app/product_ui.py` |
| Cost diary | `app/costing.py` |
| Location search | `app/location_search.py` |
| Location/solar resource | `app/location_engine.py` |
| Solar analytics | `app/solar_analytics.py` |

## Overlapping modules identified

### Engineering calculations
- `calculations.py`
- `solar_calculator.py`
- `app/app/solar_calculator.py`
- `battery_model.py`
- `inverter_model.py`

### Costing
- `cost_engine.py`
- `cost_estimator.py`
- `costing.py`

### Persistence
- `database.py`
- `library_store.py`

These are **not deleted in Stage 1B**. They remain available while their
dependencies and tests are migrated.

## Changes made in Stage 1B

1. Removed duplicate entries from `requirements.txt`.
2. Added `pytest` so the repository explicitly declares its test runner.
3. Added `app/core/module_registry.py` to document authoritative and legacy
   modules.
4. Added this architecture decision record.

## Why we are not deleting files yet

A commercial engineering application should not remove modules merely because
their names overlap. A module can be used indirectly by tests, imports, or
future code. Deletion will happen only after:

1. import/dependency mapping,
2. replacement implementation,
3. tests,
4. application smoke test,
5. removal of obsolete tests/backups where appropriate.

## Next stage

Stage 2 will create the authoritative engineering calculation model and
gradually migrate the application to it. The new model will explicitly cover
load demand, peak demand, PV derating/losses, temperature, battery capacity,
DoD, efficiency, inverter sizing, charge controller sizing, cable voltage
drop, protection and engineering validation.

## Testing rule

No feature is considered verified solely because it compiles or appears in
GitHub. It must be tested in the project's real Python environment.
