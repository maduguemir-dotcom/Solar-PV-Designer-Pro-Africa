# Stage 2D — Engineering Validation & Design Intelligence

Stage 2D adds a validation and design-quality layer above the Stage 2C professional engineering engine.

## New modules
- `app/engineering/design_intelligence.py`
- `app/engineering/design_engine_v4.py`
- `tests/test_engineering_stage2d.py`

## Capabilities
- Load, PV and inverter sanity checks
- PV-to-inverter ratio screening
- Cold Voc / controller voltage checks
- Charge-controller voltage validation
- PV DC, battery DC and AC voltage-drop screening
- Battery continuous C-rate screening
- Protection architecture presence check
- 0–100 design-quality screening score
- Professional engineering status: PASS / PASS WITH WARNINGS / REVIEW REQUIRED
- Machine-readable assumptions register

## Engineering disclaimer
These checks are screening/decision-support calculations. Final cable ampacity, protection coordination, equipment compatibility, earthing, SPD selection, installation method and compliance must be verified against manufacturer datasheets and the applicable electrical standards/codes by a suitably qualified professional.

## Migration policy
The existing Streamlit UI and `main.py` are intentionally unchanged in Stage 2D. Integration occurs only after the engineering layers have been validated and regression-tested.
