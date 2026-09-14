"""Persistence helpers for platform entities.

Repositories keep SQL out of UI code and make the Stage 4A data layer easy to
replace with a hosted relational database later without changing the models.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from .database import PlatformDatabase


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class PlatformRepository:
    def __init__(self, database: PlatformDatabase):
        self.db = database
        self.db.initialize()

    def create_user(self, email: str, full_name: str = "", user_id: Optional[str] = None) -> str:
        user_id = user_id or new_id("usr")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO users(id,email,full_name) VALUES(?,?,?)",
                (user_id, email.strip().lower(), full_name.strip()),
            )
        return user_id

    def create_organization(self, name: str, owner_user_id: str, organization_id: Optional[str] = None) -> str:
        organization_id = organization_id or new_id("org")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO organizations(id,name,owner_user_id) VALUES(?,?,?)",
                (organization_id, name.strip(), owner_user_id),
            )
            conn.execute(
                "INSERT INTO organization_members(organization_id,user_id,role) VALUES(?,?,?)",
                (organization_id, owner_user_id, "owner"),
            )
            conn.execute(
                "INSERT INTO subscriptions(id,organization_id) VALUES(?,?)",
                (new_id("sub"), organization_id),
            )
        return organization_id

    def add_member(self, organization_id: str, user_id: str, role: str = "member") -> None:
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO organization_members(organization_id,user_id,role,status) VALUES(?,?,?,?)",
                (organization_id, user_id, role, "active"),
            )

    def create_customer(self, organization_id: str, name: str, email: str = "", phone: str = "", address: str = "", notes: str = "", customer_id: Optional[str] = None) -> str:
        customer_id = customer_id or new_id("cus")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO customers(id,organization_id,name,email,phone,address,notes) VALUES(?,?,?,?,?,?,?)",
                (customer_id, organization_id, name.strip(), email.strip(), phone.strip(), address.strip(), notes.strip()),
            )
        return customer_id

    def create_project(self, organization_id: str, name: str, customer_id: Optional[str] = None, location: str = "", notes: str = "", project_id: Optional[str] = None) -> str:
        project_id = project_id or new_id("prj")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO projects(id,organization_id,customer_id,name,location,notes) VALUES(?,?,?,?,?,?)",
                (project_id, organization_id, customer_id, name.strip(), location.strip(), notes.strip()),
            )
        return project_id

    def create_design(self, project_id: str, name: str, engine_version: str = "v4", design_id: Optional[str] = None) -> str:
        design_id = design_id or new_id("dsn")
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(version), 0) AS max_version FROM designs WHERE project_id=?",
                (project_id,),
            ).fetchone()
            version = int(row["max_version"]) + 1
            conn.execute(
                "INSERT INTO designs(id,project_id,name,version,engine_version) VALUES(?,?,?,?,?)",
                (design_id, project_id, name.strip(), version, engine_version),
            )
        return design_id

    def add_design_equipment(self, design_id: str, equipment_type: str, product_id: str, quantity: int = 1, snapshot: Optional[dict[str, Any]] = None, equipment_id: Optional[str] = None) -> str:
        equipment_id = equipment_id or new_id("eqp")
        snapshot_json = json.dumps(snapshot or {}, sort_keys=True)
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO design_equipment(id,design_id,equipment_type,product_id,quantity,snapshot_json) VALUES(?,?,?,?,?,?)",
                (equipment_id, design_id, equipment_type, product_id, quantity, snapshot_json),
            )
        return equipment_id

    def save_design_result(self, design_id: str, result_type: str, result: dict[str, Any], quality_score: Optional[float] = None, result_id: Optional[str] = None) -> str:
        result_id = result_id or new_id("res")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO design_results(id,design_id,result_type,result_json,quality_score) VALUES(?,?,?,?,?)",
                (result_id, design_id, result_type, json.dumps(result, sort_keys=True, default=str), quality_score),
            )
        return result_id

    def get_subscription(self, organization_id: str) -> Optional[dict[str, Any]]:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE organization_id=? ORDER BY created_at DESC LIMIT 1",
                (organization_id,),
            ).fetchone()
        return dict(row) if row else None

    def create_subscription(self, organization_id: str, plan_code: str = "free", status: str = "active", subscription_id: Optional[str] = None) -> str:
        subscription_id = subscription_id or new_id("sub")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO subscriptions(id,organization_id,plan_code,status) VALUES(?,?,?,?)",
                (subscription_id, organization_id, plan_code, status),
            )
        return subscription_id

    def update_subscription_for_org(self, organization_id: str, plan_code: str, status: str = "active") -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE subscriptions SET plan_code=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE organization_id=?",
                (plan_code, status, organization_id),
            )

    def usage_since(self, organization_id: str, metric: str, since: str) -> int:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(quantity),0) AS total FROM usage_records WHERE organization_id=? AND metric=? AND recorded_at>=?",
                (organization_id, metric, since),
            ).fetchone()
        return int(row["total"] if row else 0)

    def record_usage(self, organization_id: str, metric: str, quantity: int = 1, usage_id: Optional[str] = None) -> str:
        usage_id = usage_id or new_id("use")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO usage_records(id,organization_id,metric,quantity) VALUES(?,?,?,?)",
                (usage_id, organization_id, metric, quantity),
            )
        return usage_id

    def list_records(self, table: str, where: str = "", params: tuple = ()) -> list[dict[str, Any]]:
        """Return records from an allow-listed platform table.

        ``where`` is intentionally caller-supplied only by internal application
        code; values belong in ``params`` so user input is never interpolated.
        """
        allowed = {"users", "organizations", "organization_members", "customers", "projects", "designs", "design_equipment", "design_results", "reports", "subscriptions", "usage_records"}
        if table not in allowed:
            raise ValueError(f"Unsupported table: {table}")
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        sql += " ORDER BY recorded_at DESC" if table == "usage_records" else " ORDER BY created_at DESC"
        with self.db.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def update_record(self, table: str, record_id: str, fields: dict[str, Any]) -> None:
        """Update a small allow-listed platform record."""
        allowed = {"users", "organizations", "customers", "projects", "designs", "subscriptions"}
        if table not in allowed:
            raise ValueError(f"Unsupported update table: {table}")
        if not fields:
            return
        allowed_fields = {
            "users": {"email", "full_name", "status"},
            "organizations": {"name", "status"},
            "customers": {"name", "email", "phone", "address", "notes"},
            "projects": {"customer_id", "name", "status", "location", "notes"},
            "designs": {"name", "status", "engine_version"},
            "subscriptions": {"plan_code", "status"},
        }
        if any(key not in allowed_fields[table] for key in fields):
            raise ValueError("Unsupported or protected field in update")
        assignments = ", ".join(f"{key}=?" for key in fields)
        values = list(fields.values()) + [record_id]
        with self.db.connect() as conn:
            conn.execute(f"UPDATE {table} SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?", values)


    def create_report(self, design_id: str, report_type: str = "engineering", status: str = "generated", report_id: Optional[str] = None) -> str:
        report_id = report_id or new_id("rpt")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO reports(id,design_id,report_type,status) VALUES(?,?,?,?)",
                (report_id, design_id, report_type, status),
            )
        return report_id

    def update_report(self, report_id: str, *, file_path: Optional[str] = None, status: Optional[str] = None) -> None:
        fields = {}
        if file_path is not None:
            fields["file_path"] = file_path
        if status is not None:
            fields["status"] = status
        if not fields:
            return
        assignments = ", ".join(f"{key}=?" for key in fields)
        with self.db.connect() as conn:
            conn.execute(f"UPDATE reports SET {assignments} WHERE id=?", list(fields.values()) + [report_id])

    def get_one(self, table: str, record_id: str) -> Optional[dict[str, Any]]:
        allowed = {"users", "organizations", "customers", "projects", "designs", "design_equipment", "design_results", "reports", "subscriptions", "usage_records"}
        if table not in allowed:
            raise ValueError(f"Unsupported table: {table}")
        id_column = "id"
        with self.db.connect() as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE {id_column}=?", (record_id,)).fetchone()
        return dict(row) if row else None

# Stage 5A authentication helpers
    def find_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
        return dict(row) if row else None

    def set_password_hash(self, user_id: str, password_hash: str) -> None:
        with self.db.connect() as conn:
            conn.execute("UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (password_hash, user_id))

    def set_email_verified(self, user_id: str, verified: bool = True) -> None:
        with self.db.connect() as conn:
            conn.execute("UPDATE users SET email_verified=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (1 if verified else 0, user_id))

    def mark_login(self, user_id: str) -> None:
        with self.db.connect() as conn:
            conn.execute("UPDATE users SET last_login_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP WHERE id=?", (user_id,))

    def memberships_for_user(self, user_id: str) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM organization_members WHERE user_id=? AND status='active' ORDER BY created_at", (user_id,)).fetchall()
        return [dict(row) for row in rows]

    def organizations_for_user(self, user_id: str) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT o.*, m.role AS member_role FROM organizations o JOIN organization_members m ON m.organization_id=o.id WHERE m.user_id=? AND m.status='active' ORDER BY o.created_at",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]
