import tempfile
from app.platform.database import PlatformDatabase
from app.services.document_service import DocumentService

def test_document_token_access_and_revocation():
    with tempfile.TemporaryDirectory() as d:
        db=PlatformDatabase(db_path=f'{d}/platform.db'); db.initialize()
        with db.connect() as conn:
            conn.execute("INSERT INTO users (id,email) VALUES ('u1','u1@example.com')")
            conn.execute("INSERT INTO organizations (id,name,owner_user_id) VALUES ('org1','Org','u1')")
            conn.execute("INSERT INTO projects (id,organization_id,name) VALUES ('p1','org1','Project')")
            conn.execute("INSERT INTO quotations (id,organization_id,project_id,quote_number,currency) VALUES ('quo1','org1','p1','Q-1','USD')")
        svc=DocumentService(db)
        out=svc.register_document('org1','quo1','reports/q.pdf')
        assert svc.validate_access(out['document_id'], out['access_token'])['storage_path']=='reports/q.pdf'
        assert svc.validate_access(out['document_id'], 'bad') is None
        PlatformDatabase
        svc.repo.revoke_proposal_document(out['document_id'])
        assert svc.validate_access(out['document_id'], out['access_token']) is None
