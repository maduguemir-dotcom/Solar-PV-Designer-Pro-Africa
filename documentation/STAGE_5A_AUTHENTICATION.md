# Stage 5A — Authentication & Organization Access

## Purpose

Stage 5A introduces the first commercial identity/access boundary around Solar PV Designer Pro Africa™.

## Added

- User password credentials using PBKDF2-HMAC-SHA256 with a per-user random salt.
- Sign-in and account-registration UI.
- Authenticated Streamlit session context.
- Organization selection for users belonging to multiple organizations.
- Roles: owner, admin, engineer, staff.
- Role/permission service boundary for future SaaS authorization.
- Migration support for Stage 4 databases by adding authentication columns when missing.
- Legacy local workspace claim: the first registered account can take ownership of the Stage 4 local workspace so existing customer/project data is not stranded.

## Security boundary

Passwords are never stored in plaintext. Only password hashes are persisted.

The current credential store is SQLite and is intended as a development/self-hosted foundation. It is **not yet the final production hosted authentication provider**. Stage 5 production deployment should move credentials/session management to a managed identity provider and hosted database.

## Organization model

Every authenticated user works through an organization membership. Organization roles are explicit and permission checks are centralized in `AuthService`.

## Files

- `app/auth/security.py`
- `app/auth/service.py`
- `app/auth/ui.py`
- `app/auth/__init__.py`
- `app/platform/schema.py`
- `app/platform/database.py`
- `app/platform/repositories.py`
- `app/ui/project_management.py`
- `app/main.py`
- `tests/test_stage5a_auth.py`

## Not included yet

- Email verification delivery
- Password reset emails
- OAuth/social login
- Hosted database
- Production session/token service
- Subscription enforcement
- Payments
