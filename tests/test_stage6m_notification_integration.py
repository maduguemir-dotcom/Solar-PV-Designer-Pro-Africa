from app.platform.database import PlatformDatabase
from app.services.proposal_portal_service import ProposalPortalService

class Events:
    def __init__(self): self.calls = []
    def dispatch(self, *args): self.calls.append(args); return {"status": "queued"}

def test_status_transition_dispatches_event(tmp_path):
    db = PlatformDatabase(tmp_path / "platform.db"); db.initialize()
    events = Events(); service = ProposalPortalService(db, events)
    with db.connect() as conn:
        conn.execute("INSERT INTO users (id,email,full_name,password_hash) VALUES ('u','u@example.com','U','x')")
        conn.execute("INSERT INTO organizations (id,name,owner_user_id) VALUES ('o','Org','u')")
        conn.execute("INSERT INTO organization_members (organization_id,user_id,role) VALUES ('o','u','owner')")
        conn.execute("INSERT INTO projects (id,organization_id,name,status) VALUES ('p','o','P','active')")
        conn.execute("INSERT INTO quotations (id,organization_id,project_id,quote_number,status,currency) VALUES ('q','o','p','Q-1','draft','USD')")
    result = service.set_status('q', 'o', 'sent', recipient='customer@example.com')
    assert result['updated'] == 1
    assert result['notification']['status'] == 'queued'
    assert events.calls[0][1] == 'proposal_sent'
