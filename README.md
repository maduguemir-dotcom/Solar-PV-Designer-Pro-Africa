# Solar PV Designer Pro Africa™ — Stage 6W

## Notification Administration Workspace Integration

Stage-only package providing the integration boundary for the notification
operations administration workspace.

### Files

```text
app/services/notification_admin_integration.py
app/ui/notification_admin_workspace.py
tests/test_stage6w_admin_integration.py
documentation/STAGE_6W_ADMIN_WORKSPACE_INTEGRATION.md
README.md
```

Upload these files into the existing `development-v3.0` project after Stage 6V.
The package intentionally does not overwrite the host application's main admin
navigation file; the existing admin entry point should call the supplied
`NotificationAdminIntegration`.

### Commit

`Stage 6W - Integrate notification operations into admin workspace`

Do not merge into `main` yet.
