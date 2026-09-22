"""Production email provider adapters; credentials are supplied at runtime."""
from __future__ import annotations
import smtplib
from email.message import EmailMessage as SMTPMessage
from app.services.email_service import EmailProvider, EmailMessage

class SMTPEmailProvider(EmailProvider):
    name = "smtp"
    def __init__(self, host: str, port: int, username: str, password: str, sender: str, use_tls: bool = True):
        self.host, self.port, self.username, self.password, self.sender, self.use_tls = host, int(port), username, password, sender, use_tls
    def send(self, message: EmailMessage) -> dict:
        mail = SMTPMessage(); mail["From"] = self.sender; mail["To"] = message.to; mail["Subject"] = message.subject
        mail.set_content(message.text_body or "")
        if message.html_body: mail.add_alternative(message.html_body, subtype="html")
        with smtplib.SMTP(self.host, self.port, timeout=20) as server:
            if self.use_tls: server.starttls()
            if self.username: server.login(self.username, self.password)
            server.send_message(mail)
        return {"provider": self.name, "status": "sent", "provider_message_id": None}
