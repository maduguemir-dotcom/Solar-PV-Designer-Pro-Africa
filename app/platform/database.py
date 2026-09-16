"""Connection and initialization layer for the platform SQLite database."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .schema import SCHEMA_SQL, SCHEMA_VERSION

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "solar_pv_platform.db"


class PlatformDatabase:
    """Small, testable SQLite wrapper for platform/business data."""

    def __init__(self, db_path: Optional[str | Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            # Lightweight migration for databases created during Stage 4.
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
            if "password_hash" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if "email_verified" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0")
            if "last_login_at" not in columns:
                conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT")
            # Stage 5B keeps the existing subscription/usage tables and adds
            # an index useful for monthly entitlement checks.
            sub_columns = {row["name"] for row in conn.execute("PRAGMA table_info(subscriptions)").fetchall()}
            if "provider_subscription_id" not in sub_columns:
                conn.execute("ALTER TABLE subscriptions ADD COLUMN provider_subscription_id TEXT")
            if "current_period_end" not in sub_columns:
                conn.execute("ALTER TABLE subscriptions ADD COLUMN current_period_end TEXT")
            # Stage 6A migrations: commercial customer/site workspace fields.
            customer_columns = {row["name"] for row in conn.execute("PRAGMA table_info(customers)").fetchall()}
            if "customer_type" not in customer_columns:
                conn.execute("ALTER TABLE customers ADD COLUMN customer_type TEXT NOT NULL DEFAULT 'individual'")
            if "contact_person" not in customer_columns:
                conn.execute("ALTER TABLE customers ADD COLUMN contact_person TEXT NOT NULL DEFAULT ''")
            project_columns = {row["name"] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
            if "site_id" not in project_columns:
                conn.execute("ALTER TABLE projects ADD COLUMN site_id TEXT")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sites_org ON sites(organization_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sites_customer ON sites(customer_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_org_metric_date ON usage_records(organization_id, metric, recorded_at)")
            conn.execute(
                "INSERT INTO schema_meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("schema_version", str(SCHEMA_VERSION)),
            )

    def schema_version(self) -> int:
        self.initialize()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT value FROM schema_meta WHERE key='schema_version'"
            ).fetchone()
            return int(row["value"]) if row else 0

    def table_names(self) -> list[str]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        return [row["name"] for row in rows]
