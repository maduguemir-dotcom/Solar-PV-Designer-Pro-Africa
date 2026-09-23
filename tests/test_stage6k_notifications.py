import json
from services.notification_preferences_service import NotificationPreferencesService

def test_defaults_and_save():
    class C:
        def __enter__(self): return self
        def __exit__(self,*a): pass
        def execute(self,*a):
            class R:
                def fetchone(self): return None
            return R()
    class DB:
        def connect(self): return C()
    svc=NotificationPreferencesService(DB())
    assert svc.get('org')['proposal_sent'] is True
