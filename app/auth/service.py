"""Authentication and organization access service.

Stage 5A deliberately keeps the provider boundary small. The local SQLite
implementation is suitable for development/demo use; Stage 5 production
hosting can replace the credential/session adapter without changing business
services or engineering code.
"""
from __future__ import annotations
from typing import Optional
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from .security import hash_password, verify_password

ROLES = ("owner", "admin", "engineer", "staff")
ROLE_PERMISSIONS = {
    "owner": {"manage_organization", "manage_team", "manage_projects", "run_designs", "manage_reports"},
    "admin": {"manage_organization", "manage_team", "manage_projects", "run_designs", "manage_reports"},
    "engineer": {"manage_projects", "run_designs", "manage_reports"},
    "staff": {"manage_projects", "manage_reports"},
}


class AuthService:
    def __init__(self, database: Optional[PlatformDatabase] = None):
        self.database = database or PlatformDatabase()
        self.repository = PlatformRepository(self.database)

    def register(self, email: str, password: str, full_name: str, organization_name: str) -> dict[str, str]:
        email = email.strip().lower()
        if not email or "@" not in email:
            raise ValueError("Enter a valid email address")
        if not full_name.strip():
            raise ValueError("Full name is required")
        if not organization_name.strip():
            raise ValueError("Organization name is required")
        password_hash = hash_password(password)
        user_id = self.repository.create_user(email, full_name)
        self.repository.set_password_hash(user_id, password_hash)
        legacy_org = self.repository.get_one("organizations", "org_local_workspace")
        if legacy_org:
            org_id = legacy_org["id"]
            # First registered user claims the pre-auth local workspace so
            # existing Stage 4 customer/project data remains accessible.
            with self.database.connect() as conn:
                conn.execute("UPDATE organizations SET owner_user_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (user_id, org_id))
            self.repository.add_member(org_id, user_id, "owner")
        else:
            org_id = self.repository.create_organization(organization_name, user_id)
        self.repository.set_email_verified(user_id, False)
        # Stage 5B: every organization enters the commercial model on FREE.
        if not self.repository.get_subscription(org_id):
            self.repository.create_subscription(org_id, "free", "active")
        return {"user_id": user_id, "organization_id": org_id}

    def authenticate(self, email: str, password: str) -> Optional[dict[str, str]]:
        user = self.repository.find_user_by_email(email.strip().lower())
        if not user or user.get("status") != "active":
            return None
        stored = user.get("password_hash") or ""
        if not stored or not verify_password(password, stored):
            return None
        self.repository.mark_login(user["id"])
        memberships = self.repository.memberships_for_user(user["id"])
        if not memberships:
            return None
        return {"user_id": user["id"], "organization_id": memberships[0]["organization_id"], "role": memberships[0]["role"], "email": user["email"], "full_name": user["full_name"]}

    def has_permission(self, role: str, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS.get(role, set())
