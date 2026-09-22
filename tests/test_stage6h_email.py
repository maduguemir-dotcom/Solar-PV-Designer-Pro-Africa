import sqlite3
from app.platform.database import PlatformDatabase
from app.services.email_service import EmailMessage, EmailService

def seed_org(db):
    with db.connect() as c:
        c.execute("INSERT INTO users(id,email,full_name) VALUES('u1','u1@example.com','User One')")
        c.execute("INSERT INTO organizations(id,name,owner_user_id) VALUES('o1','Org One','u1')")

def test_email_delivery_is_logged(tmp_path):
    db=PlatformDatabase(tmp_path/'db.sqlite')
    db.initialize(); seed_org(db)
    result=EmailService(db).send('o1', EmailMessage('customer@example.com','Hello','Body'))
    assert result['status']=='accepted'
    with db.connect() as c:
        row=c.execute('SELECT recipient, provider, status FROM email_delivery_logs').fetchone()
    assert tuple(row)==('customer@example.com','sandbox','accepted')
