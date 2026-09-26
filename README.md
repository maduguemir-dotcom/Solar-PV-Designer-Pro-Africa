# Solar PV Designer Pro Africa™ — Stage 6Z

**Stage 6Z: End-to-End Notification Security & Administration Test Suite**

This Stage-Only package contains the integration test suite and documentation for
validating the notification administration security chain from Stages 6S–6Y.

## Files

- `tests/test_stage6z_security_chain.py`
- `documentation/STAGE_6Z_SECURITY_CHAIN_TESTING.md`
- `README.md`

## Install

Extract the ZIP at the repository root or upload these files to the existing
`development-v3.0` branch. Do not replace unchanged files from earlier stages.

## Test

```bash
PYTHONPATH=. pytest -q tests/test_stage6z_security_chain.py
```

This package expects the Stage 6S–6Y modules to already exist in the branch.
Keep working on `development-v3.0`; do not merge into `main` until the full suite
and staging checks are complete.
