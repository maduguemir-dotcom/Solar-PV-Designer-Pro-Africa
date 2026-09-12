# Stage 4B — Customer & Project Management UI

## Purpose
Stage 4B exposes the Stage 4A commercial platform database through a Streamlit workspace for customers, projects and design versions.

## Added
- Customer creation and listing
- Project creation and listing
- Project status management
- Design version creation per project
- Basic workspace metrics
- Organization-scoped project/customer queries
- Local workspace bootstrap used only until authentication is introduced

## Architecture
The UI calls `ProjectService` / `PlatformRepository`. It does not write SQL directly. Product Library storage remains separate and authoritative.

## Authentication boundary
Stage 4B intentionally uses a deterministic local workspace identity because online authentication is a later stage. No passwords or credentials are stored.

## Safety
- Platform database remains separate from the Product Library database.
- User-entered values are passed as SQL parameters.
- Product records are not duplicated.
- Existing professional engineering and Product Library workflows remain intact.

## Next
Stage 4C should persist actual professional engineering design results, selected equipment references/snapshots and report metadata against saved project design versions.
