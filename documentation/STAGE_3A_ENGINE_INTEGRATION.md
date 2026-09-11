# Stage 3A — Professional Engineering Engine Integration

## Purpose

Stage 3A connects the validated v3 professional engineering engine to the existing Streamlit application while preserving the existing v2.4 workflow.

## What changed

- Added `services/professional_design_service.py` as a UI-to-engine compatibility layer.
- Existing appliance planner records are translated into the Stage 2 engineering `LoadItem` model.
- Manual daily energy has an explicit aggregate-load fallback when no appliance records are available.
- Added a separate **Professional Engineering Design** action to `app/main.py`.
- Added display of PV electrical configuration, charge controller, cables, protection, battery/system architecture, generator option, validation checks, warnings, quality score and assumptions.
- Existing PV/battery/inverter calculation workflow remains available and is not removed.

## Safety of migration

The professional engine is deliberately invoked through a separate button and stores results in a separate session-state key: `professional_design_results`. This makes the migration reversible and reduces the chance of breaking existing features.

## Engineering note

The integrated module/electrical values are indicative defaults. Final designs must use manufacturer datasheets, applicable electrical standards/codes, site conditions, earthing/lightning requirements, and competent engineering review.

## Verification

The Stage 3A service tests cover appliance translation, manual-energy fallback, and successful creation of a validated professional design result. Python compilation is also performed across the application source tree.
