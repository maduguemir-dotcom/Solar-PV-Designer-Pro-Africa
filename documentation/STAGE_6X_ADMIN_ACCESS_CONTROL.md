# Stage 6X — Production Administration Access Control Integration

Stage 6X adds the authorization boundary for the notification administration workspace.

## Rules
- Only authenticated `owner` and `admin` roles may enter the notification administration workspace.
- The actor organization must exactly match the requested organization.
- Missing identity, unsupported role, or cross-organization access raises `PermissionError` before UI rendering.
- The adapter does not implement login or session authentication; the host application remains responsible for establishing the authenticated context.

## Host integration
Pass the host-authenticated values to `NotificationAdminIntegration.render(...)`:
`actor_user_id`, `actor_role`, `actor_organization_id`, and `organization_id`.

Do not bypass this boundary by calling the notification administration UI directly from an untrusted route.
