# Solar PV Designer Pro Africa™ — Stage 1A Architecture Stabilization

## Objective

Stage 1A establishes the first controlled step from the v2.4 monolithic
Streamlit application toward a maintainable v3.0 SaaS architecture.

## Changes made

1. Added `app/core/session_state.py`
   - Centralizes default Streamlit session state.
   - Uses deep copies so mutable defaults are not accidentally shared.

2. Added `app/services/design_service.py`
   - Provides a service boundary between Streamlit UI and the existing
     calculation engine.
   - Adapts the current v2.4 calculation signatures.
   - Keeps the legacy engineering formulas unchanged in this stage.

3. Updated `app/main.py`
   - Imports the design service instead of calling the calculation functions
     directly.
   - Uses the centralized session-state initializer.
   - Fixes the existing calculation-call/signature mismatch.
   - Keeps the existing location, NASA POWER, appliance, product-library,
     cost-diary, AI and PDF-report functionality in place.

## Important engineering note

The current legacy battery calculation only accepts:

`energy, autonomy_days, battery_type`

and the current legacy inverter calculation is based on PV capacity.

Therefore Stage 1A does **not** pretend that the UI's voltage, battery-efficiency
and DoD fields are already implemented in the calculation engine. Those inputs
are retained as design metadata for the next engineering-engine stage.

Stage 2 will introduce an authoritative engineering model for:

- load/peak-demand analysis
- PV losses and derating
- temperature correction
- battery nominal/usable capacity
- battery efficiency and DoD
- inverter sizing from load and surge requirements
- charge-controller sizing
- cable/voltage-drop calculations
- protection-device sizing
- engineering validation and warnings

## What is deliberately NOT changed yet

- No user authentication
- No payments
- No subscription enforcement
- No database migration
- No deletion of legacy modules
- No external API replacement
- No change to the public GitHub repository

This is intentional: Stage 1A is a low-risk stabilization layer before the
database and multi-user architecture are introduced.

## Testing status

The source changes should be syntax-checked in the user's own Anaconda/
Python environment with the project's installed dependencies. The previous
isolated audit environment could not install Streamlit because it had no
external package access, so dependency-level tests were not claimed as passed.
