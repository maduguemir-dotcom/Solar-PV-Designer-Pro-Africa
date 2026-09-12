# Stage 4A — Users, Organizations & Projects

## Objective

Stage 4A introduces the persistent business/platform data layer required to evolve Solar PV Designer Pro Africa™ from a single-user engineering application into a multi-user commercial SaaS platform.

## Architecture

```text
User
  │
  └── Organization ── Organization Members
          │
          ├── Customers
          │     └── Projects
          │           └── Designs
          │                 ├── Design Equipment → Product Library IDs
          │                 ├── Design Results
          │                 └── Reports
          │
          ├── Subscription
          └── Usage Records
```

## New platform database

`app/platform/database.py` creates a separate SQLite database:

`app/data/solar_pv_platform.db`

This database **does not replace or duplicate** the existing Product Library database. Product Library remains the authoritative source for equipment records. Design equipment records reference Product Library product IDs and may keep an immutable JSON snapshot when a design is saved.

## Tables

- `users`
- `organizations`
- `organization_members`
- `customers`
- `projects`
- `designs`
- `design_equipment`
- `design_results`
- `reports`
- `subscriptions`
- `usage_records`
- `schema_meta`

## Design principles

1. Authentication is intentionally **not** implemented in Stage 4A.
2. Payment processing is intentionally **not** implemented in Stage 4A.
3. The engineering engine remains separate from platform persistence.
4. Product Library remains the product authority.
5. Design records are versioned per project.
6. Foreign keys are enforced by SQLite.
7. Repository/service layers keep SQL away from Streamlit UI code.
8. The schema is deliberately portable to PostgreSQL or another hosted relational database in a later SaaS stage.

## Workflow enabled

```text
onboard user
   ↓
create organization
   ↓
create customer
   ↓
create project
   ↓
create design/version
   ↓
attach selected Product Library equipment
   ↓
save engineering result
   ↓
record usage
```

## What is deliberately deferred

- Login/password/OAuth
- Email verification
- Team invitations UI
- Role/permission enforcement beyond stored roles
- Online PostgreSQL deployment
- Stripe/payment integration
- Subscription billing automation
- Usage-limit enforcement
- Customer/project dashboard UI

Those belong to later commercial SaaS stages after this persistence foundation is validated.
