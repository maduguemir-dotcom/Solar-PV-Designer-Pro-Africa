# Stage 3D — Professional Equipment Selection UI

Stage 3D connects the central Product Library to a Streamlit equipment-selection workflow.

## Workflow

1. Select a PV module, battery and inverter from the Product Library.
2. Optionally select a charge controller.
3. Review engineering-data completeness.
4. Validate equipment compatibility.
5. Store the validated selection in the current design session.
6. The Professional Engineering Design uses the selected PV/battery/controller electrical specifications instead of generic defaults.

## Safeguards

- The existing central Product Library remains the only persistent product source.
- Missing technical specifications are reported rather than invented.
- PV module, battery and inverter are required for validation.
- Charge controller is optional; the inverter MPPT window is used when it is not selected.
- Legacy/manual design remains available when no equipment selection is made.
- Equipment selection is a design input, not a certification of installation compliance.
