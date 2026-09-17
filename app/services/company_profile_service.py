"""Organization branding and commercial profile service."""
from __future__ import annotations
from typing import Any

class CompanyProfileService:
    def __init__(self, repository):
        self.repository = repository

    def get(self, organization_id: str) -> dict[str, Any]:
        return self.repository.get_organization_profile(organization_id) or {
            "organization_id": organization_id, "legal_name": "", "display_name": "",
            "logo_path": "", "address": "", "phone": "", "email": "", "website": "",
            "tax_id": "", "payment_terms": "", "quotation_validity_days": 30,
            "bank_details": "", "terms_conditions": ""
        }

    def save(self, organization_id: str, **fields) -> None:
        self.repository.save_organization_profile(organization_id, fields)
