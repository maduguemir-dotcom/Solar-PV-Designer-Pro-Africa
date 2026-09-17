"""Persistence boundary for Stage 6B quotations."""
from __future__ import annotations

import json
from app.platform.repositories import PlatformRepository, new_id
from app.platform.database import PlatformDatabase


class QuotationPersistenceService:
    def __init__(self, database=None):
        self.db = database or PlatformDatabase()
        self.repo = PlatformRepository(self.db)

    def create_quote(self, organization_id: str, project_id: str, quote_number: str,
                    quote: dict, *, customer_id=None, status="draft") -> str:
        quote_id = new_id("quo")
        with self.db.connect() as conn:
            conn.execute("""INSERT INTO quotations
                (id,organization_id,project_id,customer_id,quote_number,status,currency,
                 direct_cost,overhead,contingency,markup,subtotal,tax,grand_total,
                 assumptions_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (quote_id, organization_id, project_id, customer_id, quote_number.strip(), status,
                 quote["quote_currency"], quote["direct_cost"], quote["overhead"],
                 quote["contingency"], quote["markup"], quote["subtotal"], quote["tax"],
                 quote["grand_total"], json.dumps({k: quote[k] for k in (
                     "overhead_percent","contingency_percent","markup_percent","tax_percent")}, sort_keys=True)))
            for line in quote.get("lines", []):
                conn.execute("""INSERT INTO quotation_items
                    (id,quotation_id,category,description,quantity,unit,unit_price,currency,fx_rate,total)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (new_id("qit"), quote_id, line["category"], line["description"], line["quantity"],
                     line["unit"], line["unit_price"], line["currency"], line["fx_rate"], line["total"]))
        return quote_id
