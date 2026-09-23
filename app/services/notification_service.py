"""Environment-selected email notifications with durable queue records."""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
from app.services.email_service import EmailMessage, EmailService, SandboxEmailProvider
from app.billing.production_email import SMTPEmailProvider

EVENTS = ("proposal_sent", "proposal_accepted", "proposal_rejected")

def provider_from_environment():
    name = os.getenv("EMAIL_PROVIDER", "sandbox").lower()
    if name == "smtp":
        return SMTPEmailProvider(os.environ["EMAIL_SMTP_HOST"], int(os.getenv("EMAIL_SMTP_PORT", "587")), os.getenv("EMAIL_SMTP_USERNAME", ""), os.environ["EMAIL_SMTP_PASSWORD"], os.environ["EMAIL_SENDER"], os.getenv("EMAIL_SMTP_USE_TLS", "true").lower() == "true")
    return SandboxEmailProvider()

class NotificationService:
    def __init__(self, database=None, email_service=None):
        self.email = email_service or EmailService(database=database, provider=provider_from_environment())
        self.db = self.email.db

    def queue_notification(self, organization_id, recipient, subject, text_body, html_body="", event_type="notification"):
        if event_type not in EVENTS and event_type != "notification":
            raise ValueError("Unsupported notification event")
        notification_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self.db.connect() as conn:
            conn.execute("INSERT INTO notification_queue (id, organization_id, recipient, subject, text_body, html_body, event_type, status, attempts, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, ?)", (notification_id, organization_id, recipient, subject, text_body, html_body, event_type, now))
        return notification_id

    def deliver(self, notification_id):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM notification_queue WHERE id=?", (notification_id,)).fetchone()
            if not row: raise ValueError("Notification not found")
            if row["status"] == "sent": return {"status": "sent", "id": notification_id}
            conn.execute("UPDATE notification_queue SET attempts=attempts+1, status='processing' WHERE id=?", (notification_id,))
        try:
            result = self.email.send(row["organization_id"], EmailMessage(row["recipient"], row["subject"], row["text_body"], row["html_body"]), row["event_type"])
            status = "sent" if result.get("status") in ("sent", "accepted") else "failed"
            with self.db.connect() as conn: conn.execute("UPDATE notification_queue SET status=?, last_error=NULL WHERE id=?", (status, notification_id))
            return {"id": notification_id, **result}
        except Exception as exc:
            with self.db.connect() as conn: conn.execute("UPDATE notification_queue SET status='failed', last_error=? WHERE id=?", (str(exc), notification_id))
            raise
