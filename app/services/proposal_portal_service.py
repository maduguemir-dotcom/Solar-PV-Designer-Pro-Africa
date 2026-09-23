"""Customer-facing proposal portal workflow with notification integration."""
from __future__ import annotations
from app.services.document_service import DocumentService

class ProposalPortalService:
    STATUSES = ("draft", "sent", "viewed", "accepted", "rejected", "expired")

    def __init__(self, database=None, notification_events=None):
        self.documents = DocumentService(database)
        self.db = self.documents.db
        self.repo = self.documents.repo
        self.notification_events = notification_events

    def set_status(self, quotation_id: str, organization_id: str, status: str, *, recipient=None, subject=None, text_body=None, html_body="") -> dict:
        if status not in self.STATUSES:
            raise ValueError("Unsupported proposal status")
        with self.db.connect() as conn:
            cur = conn.execute("UPDATE quotations SET status=? WHERE id=? AND organization_id=?", (status, quotation_id, organization_id))
        result = {"updated": cur.rowcount, "status": status}
        event_type = {"sent": "proposal_sent", "accepted": "proposal_accepted", "rejected": "proposal_rejected"}.get(status)
        if cur.rowcount and event_type and self.notification_events and recipient:
            result["notification"] = self.notification_events.dispatch(
                organization_id, event_type, recipient,
                subject or f"Proposal {status}",
                text_body or f"Your proposal status is now {status}.", html_body
            )
        return result

    def create_share_link(self, organization_id: str, quotation_id: str, storage_path: str, expires_at=None) -> dict:
        return self.documents.register_document(organization_id, quotation_id, storage_path, expires_at=expires_at, document_type="proposal")

    def access(self, document_id: str, token: str, metadata=None) -> dict | None:
        doc = self.documents.validate_access(document_id, token)
        if doc is None:
            return None
        self.documents.record_access(document_id, "view", metadata)
        return doc
