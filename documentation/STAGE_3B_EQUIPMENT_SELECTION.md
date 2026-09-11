# Stage 3B — Professional Design Input & Equipment Selection

Stage 3B introduces typed, equipment-aware design inputs without coupling the engineering layer to Streamlit.

## Added
- `app/equipment/schemas.py`: PV module, battery, inverter, charge-controller and cable specifications.
- `app/equipment/selection.py`: compatibility checks.
- `app/services/equipment_design_service.py`: equipment-aware orchestration.
- Automated Stage 3B tests.

## Design rule
Equipment specifications should ultimately come from the Product Library/manufacturer datasheets. Default values are indicative engineering-screening defaults and must not be treated as manufacturer-certified specifications.

## Migration strategy
Stage 3B does not replace the existing Product Library or Streamlit UI. It establishes a clean contract so Stage 3C can connect selected library products to the professional engine.
