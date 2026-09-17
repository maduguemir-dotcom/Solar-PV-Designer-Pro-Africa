# Stage 6B — Cost Estimation & Quotation Engine

## Purpose
Stage 6B adds a persistent commercial costing layer without replacing the existing Product Library or Cost Diary.

## Features
- Explicit project cost lines
- Quantity, unit price and source currency
- User-supplied foreign-exchange conversion to quotation currency
- Overhead, contingency, markup and tax calculations
- Direct cost, cost base, subtotal and customer total
- Gross-margin value and percentage-of-sale calculation
- Persistent quotations and quotation line items
- Quote number uniqueness per organization
- Draft/issued/accepted/rejected/expired statuses
- Subscription-controlled quotation creation

## Currency policy
The system does not invent live exchange rates. If a line is priced in a different currency, the user supplies the FX rate used for the quotation and that assumption is retained with the quote.

## Architecture
Product Library remains the authoritative source for product records. The quotation engine stores the commercial price actually used for a project; it does not duplicate the Product Library database.

Platform schema version: 7.
