from app.platform.database import PlatformDatabase
from app.services.notification_service import NotificationService

def test_queue_and_deliver(tmp_path):
    db = PlatformDatabase(tmp_path / "x.db"); db.initialize()
    with db.connect() as c:
        c.execute("INSERT INTO users(id, email, full_name) VALUES ('u1','u1@example.com','User')")
        c.execute("INSERT INTO organizations(id, name, owner_user_id) VALUES ('o1','Org','u1')")
    svc = NotificationService(database=db)
    nid = svc.queue_notification('o1','test@example.com','Subject','Body')
    result = svc.deliver(nid)
    assert result['status'] == 'accepted'
