# Stage 4C — Design Persistence & Project History

Stage 4C connects the professional engineering result to the Stage 4A/4B platform database.

## Added
- `services/design_persistence_service.py`: transactional application workflow for saving professional designs, equipment references, engineering results and usage.
- `ui/design_persistence.py`: Streamlit save/history entry point.
- `main.py`: professional design results now expose a **Save to Customer Project & Design History** panel.
- tests covering result persistence, equipment references, usage records and design versioning.

## Data rules
- Product Library remains the authoritative product store.
- `design_equipment.product_id` references Product Library IDs; a compact immutable snapshot is retained with the saved design for historical reproducibility.
- Engineering results are stored as JSON under `design_results` so the engine can evolve without flattening every engineering field into platform tables.
- Saving creates a new design version by default. Existing design records can be updated explicitly from the UI.

## Not included
Authentication, online payments, hosted database migration and cloud file storage remain later SaaS stages.
