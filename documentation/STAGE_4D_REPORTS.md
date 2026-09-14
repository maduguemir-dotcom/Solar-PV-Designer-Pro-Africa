# Stage 4D — Professional Reports & Deliverables

## Purpose
Connect saved engineering designs to registered professional PDF reports.

## Delivered
- Professional report service for saved engineering designs.
- Report records linked to `designs`.
- Generated PDF is saved under the local `reports/` directory and remains downloadable in the active application session.
- Report usage is recorded against the organization.
- Report UI allows selecting a project and saved design before generation.
- Existing legacy report generator remains available; its recommendations argument is now optional to preserve compatibility with the current main application call.

## Architecture
The report service reads the saved design result and equipment references from the platform database. Product Library records are not duplicated.

## Important deployment note
The local PDF path is an application-runtime artifact. For production SaaS, Stage 5+ should move report files to durable object storage and retain only the storage reference in the database.
