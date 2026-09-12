# Stage 3C — Product Library → Engineering Engine

## Objective
Connect the existing central Product Library to the professional engineering equipment model without creating a second product database.

## Added
- `app/equipment/product_adapter.py`: converts normalized library records into engineering specs.
- `app/services/product_library_engine.py`: selects products by library ID and validates engineering compatibility.
- `tests/test_product_library_engine.py`: adapter validation tests.

## Safety principle
Missing engineering fields are reported as errors. The adapter does not invent manufacturer specifications. This is important for professional engineering use.

## Supported categories
- Solar Panel
- Battery
- Inverter
- Charge Controller

## Migration strategy
Existing product records remain untouched. The adapter is read-only and non-destructive. Future UI stages can expose only engineering-ready records and show missing-field diagnostics for incomplete records.

## Charge controller note
The existing Product Library schema does not currently contain a minimum MPPT voltage field. Stage 3C therefore requires this field before a charge controller can be used in the professional engineering engine rather than guessing a value.
