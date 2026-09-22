from __future__ import annotations
from pathlib import Path
from typing import Any

def company_display_name(company: dict[str, Any]) -> str:
    return (company.get('display_name') or company.get('legal_name') or company.get('name') or 'Solar PV Designer Pro Africa™').strip()

def company_contact_lines(company: dict[str, Any]) -> list[str]:
    pairs = [('Address', company.get('address')), ('Phone', company.get('phone')), ('Email', company.get('email')), ('Website', company.get('website')), ('Tax/VAT ID', company.get('tax_id'))]
    return [f'{label}: {value}' for label, value in pairs if value]

def resolve_logo(company: dict[str, Any]) -> str | None:
    raw = company.get('logo_path')
    if not raw: return None
    path = Path(str(raw)).expanduser()
    return str(path) if path.is_file() else None
