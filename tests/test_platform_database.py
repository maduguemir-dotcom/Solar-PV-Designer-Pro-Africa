from pathlib import Path

from app.platform.database import PlatformDatabase


def test_platform_database_initializes_expected_tables(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db")
    db.initialize()
    tables = set(db.table_names())
    expected = {
        "schema_meta", "users", "organizations", "organization_members",
        "customers", "projects", "designs", "design_equipment",
        "design_results", "reports", "subscriptions", "usage_records",
    }
    assert expected.issubset(tables)
    assert db.schema_version() == 7


def test_platform_database_foreign_keys_are_enabled(tmp_path: Path):
    db = PlatformDatabase(tmp_path / "platform.db")
    with db.connect() as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
