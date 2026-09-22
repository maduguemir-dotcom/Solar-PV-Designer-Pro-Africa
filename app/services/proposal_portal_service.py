"""Customer-facing proposal portal workflow with organization-safe access."""
from __future__ import annotations
from datetime import datetime, timezone
from app.services.document_service import DocumentService

class ProposalPortalService:
    STATUSES = ("draft", "sent", "viewed", "accepted", "rejected", "expired")
    def __init__(self, database=None):
        self.documents = DocumentService(database)
        self.db = self.documents.db
        self.repo = self.documents.repo

    def set_status(self, quotation_id: str, organization_id: str, status: str) -> int:
        if status not in self.STATUSES:
            raise ValueError("Unsupported proposal status")
        with self.db.connect() as conn:
            cur = conn.execute("UPDATE quotations SET status=? WHERE id=? AND organization_id=?", (status, quotation_id, organization_id))
            return cur.rowcount

    def create_share_link(self, organization_id: str, quotation_id: str, storage_path: str, expires_at=None) -> dict:
        return self.documents.register_document(organization_id, quotation_id, storage_path, expires_at=expires_at, document_type="proposal")

    def access(self, document_id: str, token: str, metadata=None) -> dict | None:
        doc = self.documents.validate_access(document_id, token)
        if doc is None:
            return None
        self.documents.record_access(document_id, "view", metadata)
        return doc
