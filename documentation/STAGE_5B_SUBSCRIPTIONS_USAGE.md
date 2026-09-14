# Stage 5B — Subscription Plans & Usage Controls

## Objective

Stage 5B establishes the commercial entitlement layer for Solar PV Designer Pro Africa™ without connecting a payment provider yet.

## Plans

### FREE
- 10 customers
- 3 projects
- 10 design runs/month
- 3 saved professional designs/month
- 3 professional reports/month
- 5 design versions/month
- 1 team member
- Basic design, reports and equipment access

### PROFESSIONAL
- 250 customers
- 100 projects
- 250 design runs/month
- 100 saved professional designs/month
- 100 professional reports/month
- 250 design versions/month
- 5 team members
- Advanced design, professional reports, equipment library, history and AI assistance

### BUSINESS
- Unlimited customers, projects, design runs, saved designs, reports and design versions
- Up to 25 team members in this initial commercial model
- Team management, branded reports and business analytics feature flags

## Usage model

Usage is stored in the platform database by organization and metric. Monthly limits are evaluated from the first day of the current UTC calendar month. Existing Stage 4/5A data remains in the same platform database.

## Enforcement points

Stage 5B enforces limits when creating:
- customers
- projects
- design versions
- saved professional designs
- persisted professional reports

Updating an existing saved design does not consume another saved-design entitlement.

## Payment boundary

No card charging, payment gateway, invoice collection or external billing API is implemented in Stage 5B. The subscription service is deliberately isolated so Stage 5C can attach a payment provider without changing engineering calculations or the Product Library.

## Migration safety

The platform schema advances to version 3. The existing `subscriptions` and `usage_records` tables are retained, and an additional usage index is created. New organizations continue to default to FREE.
