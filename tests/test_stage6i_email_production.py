from app.services.email_templates import proposal_sent_template, proposal_status_template
from app.billing.production_email import SMTPEmailProvider

def test_templates():
    msg = proposal_sent_template("Acme", "Amina", "https://example.test/p/abc")
    assert msg.key == "proposal_sent"
    assert "Acme" in msg.subject and "https://example.test" in msg.text_body
    status = proposal_status_template("Acme", "Amina", "Accepted")
    assert "accepted" in status.text_body

def test_smtp_provider_configuration():
    provider = SMTPEmailProvider("localhost", 587, "u", "p", "from@example.com")
    assert provider.name == "smtp"
    assert provider.port == 587
