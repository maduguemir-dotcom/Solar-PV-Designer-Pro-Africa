# Stage 6P — Stage-Only Package

Upload only these files to `development-v3.0`:

- `app/services/notification_operations_service.py`
- `app/ui/notification_operations.py`
- `tests/test_stage6p_operations.py`
- `documentation/STAGE_6P_NOTIFICATION_OPERATIONS.md`

Commit: `Stage 6P - Add notification operations dashboard and recovery controls`

Do not merge into `main`.

**Integration note:** Add the UI to the authenticated navigation and enforce role permissions before exposing recovery actions. The service itself scopes all operations by organization ID.
