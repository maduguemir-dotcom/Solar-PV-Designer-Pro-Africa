"""Secure proposal document registration and access-token handling."""
from __future__ import annotations
import hashlib, hmac, json, secrets
from datetime import datetime, timezone
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository, new_id

class DocumentService:
    def __init__(self, database=None):
        self.db = database or PlatformDatabase()
        self.repo = PlatformRepository(self.db)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def register_document(self, organization_id: str, quotation_id: str, storage_path: str, *, expires_at=None, document_type='proposal') -> dict:
        if not organization_id or not quotation_id or not storage_path:
            raise ValueError('organization_id, quotation_id and storage_path are required')
        token = secrets.token_urlsafe(32)
        document_id = new_id('doc')
        with self.db.connect() as conn:
            conn.execute('''INSERT INTO proposal_documents
                (id, organization_id, quotation_id, document_type, storage_path, access_token_hash, expires_at)
                VALUES (?,?,?,?,?,?,?)''', (document_id, organization_id, quotation_id, document_type, storage_path, self._hash_token(token), expires_at))
        return {'document_id': document_id, 'access_token': token, 'expires_at': expires_at}

    def validate_access(self, document_id: str, token: str) -> dict | None:
        doc = self.repo.get_one('proposal_documents', document_id)
        if not doc or doc.get('status') != 'active' or not token:
            return None
        if not hmac.compare_digest(doc.get('access_token_hash') or '', self._hash_token(token)):
            return None
        if doc.get('expires_at'):
            try:
                expiry = datetime.fromisoformat(doc['expires_at'].replace('Z', '+00:00'))
                if expiry.tzinfo is None: expiry = expiry.replace(tzinfo=timezone.utc)
                if expiry <= datetime.now(timezone.utc): return None
            except ValueError:
                return None
        return doc

    def record_access(self, document_id: str, event_type='view', metadata=None) -> None:
        with self.db.connect() as conn:
            conn.execute('''INSERT INTO proposal_access_events (id, document_id, event_type, metadata_json)
                            VALUES (?,?,?,?,?)'''.replace('VALUES (?,?,?,?,?)','VALUES (?,?,?,?)'),
                         (new_id('acc'), document_id, event_type, json.dumps(metadata or {}, sort_keys=True)))
