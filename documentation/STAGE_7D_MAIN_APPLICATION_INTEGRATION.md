# Stage 7D — Main Application Integration

## Changes

- Adds **Notification Administration** to the existing Streamlit navigation in `app/main.py`.
- Adds a host entry point that composes the existing notification health, audit history, audit-derived reliability, and secure recovery modules.
- Re-resolves the authenticated user's role from the persisted membership for the currently selected organization. Access remains restricted by `NotificationAdminAccess` to `owner` and `admin` roles and the selected organization scope.
- Uses the existing `PlatformDatabase`; no second database is introduced.
- Makes `DurableAuditService.list_events()` return dictionaries, matching the `.get()` usage in audit history and analytics consumers.
- Leaves the existing solar engineering pages and the `main` branch untouched.

## Files

- `app/main.py` (modified)
- `app/ui/notification_admin_entry.py` (new)
- `app/services/durable_audit_service.py` (modified)
- `tests/test_stage7d_main_integration.py` (new)
- `documentation/STAGE_7D_MAIN_APPLICATION_INTEGRATION.md` (new)
- `README.md` (stage instructions)

## Apply

Upload the files to the working branch `stage-7d-integration`, preserving their paths. Do not commit directly to `main`. Review the diff and run the tests before merging anything back into `development-v3.0`.

## Validate

From the repository root, with the project virtual environment active:

```powershell
python -m pytest -q tests/test_stage7d_main_integration.py
python -m py_compile app/main.py app/ui/notification_admin_entry.py app/services/durable_audit_service.py
python -m streamlit run app/main.py
```

Then sign in using an account with an `owner` or `admin` role, select its organization, and open **Notification Administration**. Verify that an `engineer` or `staff` account is denied. Test recovery controls only in a development/test database.

## Important notes

- The admin workspace is not a substitute for reviewing production deployment, queue-worker behavior, email-provider configuration, or database backup/security controls.
- The audit analytics are derived from audit events; they are not direct provider-delivery statistics.
- `PlatformDatabase.initialize()` is called before using the audit and queue tables, so the schema is initialized using the application's existing schema manager.
