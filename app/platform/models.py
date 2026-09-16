"""Dataclasses representing the commercial platform's core records.

These models intentionally contain business/platform metadata rather than
engineering formulas. Engineering results remain owned by app.engineering.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    id: str
    email: str
    full_name: str = ""
    status: str = "active"


@dataclass(frozen=True)
class Organization:
    id: str
    name: str
    owner_user_id: str
    status: str = "active"


@dataclass(frozen=True)
class OrganizationMember:
    organization_id: str
    user_id: str
    role: str = "member"
    status: str = "active"


@dataclass(frozen=True)
class Customer:
    id: str
    organization_id: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Site:
    id: str
    organization_id: str
    name: str
    customer_id: Optional[str] = None
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: str = ""


@dataclass(frozen=True)
class Project:
    id: str
    organization_id: str
    name: str
    customer_id: Optional[str] = None
    site_id: Optional[str] = None
    status: str = "draft"
    location: str = ""
    notes: str = ""


@dataclass(frozen=True)
class Design:
    id: str
    project_id: str
    name: str
    version: int = 1
    status: str = "draft"
    engine_version: str = "v4"


@dataclass(frozen=True)
class DesignEquipment:
    id: str
    design_id: str
    equipment_type: str
    product_id: str
    quantity: int = 1
    snapshot_json: str = ""


@dataclass(frozen=True)
class DesignResult:
    id: str
    design_id: str
    result_type: str
    result_json: str
    quality_score: Optional[float] = None
    status: str = "completed"


@dataclass(frozen=True)
class Report:
    id: str
    design_id: str
    report_type: str = "engineering"
    file_path: str = ""
    status: str = "generated"


@dataclass(frozen=True)
class Subscription:
    id: str
    organization_id: str
    plan_code: str = "free"
    status: str = "active"


@dataclass(frozen=True)
class UsageRecord:
    id: str
    organization_id: str
    metric: str
    quantity: int = 1
