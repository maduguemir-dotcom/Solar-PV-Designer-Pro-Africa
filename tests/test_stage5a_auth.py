import sqlite3
from app.auth.security import hash_password, verify_password
from app.auth.service import AuthService
from app.platform.database import PlatformDatabase


def test_password_hashing_and_verification():
    encoded = hash_password("StrongPass123!")
    assert encoded != "StrongPass123!"
    assert verify_password("StrongPass123!", encoded)
    assert not verify_password("wrong-password", encoded)


def test_registration_login_and_organization(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    auth = AuthService(db)
    result = auth.register("Engineer@Example.com", "StrongPass123!", "Engineer One", "Example Solar Ltd")
    identity = auth.authenticate("engineer@example.com", "StrongPass123!")
    assert identity is not None
    assert identity["user_id"] == result["user_id"]
    assert identity["organization_id"] == result["organization_id"]
    assert identity["role"] == "owner"


def test_legacy_workspace_is_claimed(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db")
    auth = AuthService(db)
    old = auth.repository.create_user("workspace@solar-pv-designer.local", "Workspace User", "usr_local_workspace")
    org = auth.repository.create_organization("My Solar Design Workspace", old, "org_local_workspace")
    result = auth.register("new@example.com", "StrongPass123!", "New Owner", "New Company")
    assert result["organization_id"] == org
    assert auth.repository.get_one("organizations", org)["owner_user_id"] == result["user_id"]
