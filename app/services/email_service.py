"""Provider-independent email delivery service for proposal notifications."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    text_body: str
    html_body: str = ""

class EmailProvider:
    name = "base"
    def send(self, message: EmailMessage) -> dict:
        raise NotImplementedError

class SandboxEmailProvider(EmailProvider):
    name = "sandbox"
    def send(self, message: EmailMessage) -> dict:
        return {"provider": self.name, "status": "accepted", "provider_message_id": f"sandbox-{uuid.uuid4().hex}"}

class EmailService:
    def __init__(self, database=None, provider: EmailProvider | None = None):
        if database is None:
            from app.platform.database import PlatformDatabase
            database = PlatformDatabase()
        self.db = database
        self.provider = provider or SandboxEmailProvider()

    def send(self, organization_id: str, message: EmailMessage, event_type: str = "notification") -> dict:
        if not message.to or "@" not in message.to:
            raise ValueError("A valid recipient email is required")
        result = self.provider.send(message)
        email_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO email_delivery_logs "
                "(id, organization_id, recipient, subject, event_type, provider, status, provider_message_id, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (email_id, organization_id, message.to, message.subject, event_type,
                 result.get("provider", self.provider.name), result.get("status", "accepted"),
                 result.get("provider_message_id"), now),
            )
        return {"id": email_id, **result}
