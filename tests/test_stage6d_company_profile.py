import tempfile
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository
from app.services.company_profile_service import CompanyProfileService

def test_company_profile_round_trip():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        repo = PlatformRepository(PlatformDatabase(f.name))
        user = repo.create_user("owner@example.com", "Owner")
        org = repo.create_organization("Test Company", user)
        service = CompanyProfileService(repo)
        service.save(org, display_name="Test Solar", email="info@example.com", quotation_validity_days=45)
        profile = service.get(org)
        assert profile["display_name"] == "Test Solar"
        assert profile["email"] == "info@example.com"
        assert profile["quotation_validity_days"] == 45
