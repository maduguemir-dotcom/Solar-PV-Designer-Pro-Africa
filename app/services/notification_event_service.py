"""Preference-aware proposal notification event dispatcher."""
from __future__ import annotations
from .notification_preferences_service import NotificationPreferencesService

class NotificationEventService:
    def __init__(self, database, notification_service):
        self.preferences = NotificationPreferencesService(database)
        self.notifications = notification_service

    def dispatch(self, organization_id, event_type, recipient, subject, text_body, html_body=""):
        if not self.preferences.enabled(organization_id, event_type):
            return {"status": "skipped", "reason": "disabled", "event_type": event_type}
        notification_id = self.notifications.queue_notification(
            organization_id=organization_id,
            recipient=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            event_type=event_type,
        )
        return {"status": "queued", "notification_id": notification_id, "event_type": event_type}
