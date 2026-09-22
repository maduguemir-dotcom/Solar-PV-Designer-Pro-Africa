"""Safe, provider-neutral notification templates."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class NotificationTemplate:
    key: str
    subject: str
    text_body: str
    html_body: str

def proposal_sent_template(company: str, recipient_name: str, access_url: str) -> NotificationTemplate:
    company = company.strip() or "Solar PV Designer Pro Africa"
    name = recipient_name.strip() or "Customer"
    return NotificationTemplate(
        key="proposal_sent",
        subject=f"Your solar proposal from {company}",
        text_body=(f"Dear {name},\n\nYour solar proposal from {company} is ready for review.\n"
                   f"Open it here: {access_url}\n\nRegards,\n{company}"),
        html_body=(f"<p>Dear {name},</p><p>Your solar proposal from <strong>{company}</strong> "
                   f"is ready for review.</p><p><a href=\"{access_url}\">Review proposal</a></p>"
                   f"<p>Regards,<br>{company}</p>"),
    )

def proposal_status_template(company: str, recipient_name: str, status: str) -> NotificationTemplate:
    company = company.strip() or "Solar PV Designer Pro Africa"
    name = recipient_name.strip() or "Customer"
    status = status.strip().lower()
    return NotificationTemplate(
        key="proposal_status",
        subject=f"Proposal status update - {company}",
        text_body=f"Dear {name},\n\nYour proposal status is now: {status}.\n\nRegards,\n{company}",
        html_body=f"<p>Dear {name},</p><p>Your proposal status is now: <strong>{status}</strong>.</p><p>Regards,<br>{company}</p>",
    )
