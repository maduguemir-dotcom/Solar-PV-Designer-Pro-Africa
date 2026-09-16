# Stage 6A — Professional Customer & Company Workspace

## Objective
Strengthen the commercial workflow from customer → site → project → design while preserving existing engineering, authentication, subscription and billing functionality.

## Delivered
- Added organization-scoped installation sites.
- A customer can have multiple sites.
- Projects can reference a customer and installation site.
- Customer records now distinguish individual/company/government/NGO/other and store a contact person.
- Added site usage entitlements to FREE, PROFESSIONAL and BUSINESS plans.
- Added Sites to the Customers & Projects workspace and dashboard metrics.
- Added migration logic so existing Stage 5 databases receive the new fields without destructive replacement.

## Commercial workflow
Customer → Installation Site → Project → Design Version → Equipment → Engineering Result → Report

## Compatibility
Product Library remains a separate authoritative database. Existing designs and projects remain valid; new site_id/customer fields are additive.

## Testing
Stage 6A adds focused workspace tests. The complete suite should be run before deployment.
