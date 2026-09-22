from app.services.proposal_portal_service import ProposalPortalService

def test_statuses_are_defined():
    assert "sent" in ProposalPortalService.STATUSES
    assert "accepted" in ProposalPortalService.STATUSES
