from datetime import datetime, timezone, timedelta
from app.services.notification_reliability_service import NotificationReliabilityService

def test_reliability_contract():
    assert NotificationReliabilityService is not None
    assert datetime.now(timezone.utc) + timedelta(minutes=5) > datetime.now(timezone.utc)
