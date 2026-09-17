import pytest
from app.services.quotation_service import CostLine, calculate_quote
from app.services.quotation_persistence_service import QuotationPersistenceService
from app.platform.database import PlatformDatabase
from app.platform.repositories import PlatformRepository


def test_multi_currency_quote_and_adjustments():
    lines = [
        CostLine("PV", "Panels", 10, 100, "USD", 1),
        CostLine("Labour", "Installation", 2, 50000, "UGX", 0.00028, "day"),
    ]
    q = calculate_quote(lines, quote_currency="USD", overhead_percent=5, contingency_percent=10, markup_percent=20, tax_percent=18)
    assert q["direct_cost"] == 1028.0
    assert q["grand_total"] > q["subtotal"]
    assert len(q["lines"]) == 2


def test_requires_fx_for_different_currency():
    with pytest.raises(ValueError):
        CostLine("PV", "Panel", 1, 100, "UGX", 0).validate("USD")


def test_negative_percentage_rejected():
    with pytest.raises(ValueError):
        calculate_quote([CostLine("PV", "Panel", 1, 100)], markup_percent=-1)


def test_quote_persistence(tmp_path):
    db = PlatformDatabase(str(tmp_path / "platform.db"))
    repo = PlatformRepository(db)
    uid = repo.create_user("owner@example.com", "Owner")
    oid = repo.create_organization("Solar Co", uid)
    cid = repo.create_customer(oid, "Customer")
    pid = repo.create_project(oid, "Project", cid)
    q = calculate_quote([CostLine("PV", "Panel", 1, 100)], quote_currency="USD")
    qid = QuotationPersistenceService(db).create_quote(oid, pid, "QT-001", q, customer_id=cid)
    row = repo.get_one("quotations", qid)
    assert row["quote_number"] == "QT-001"
    assert row["grand_total"] == 100
    assert len(repo.list_records("quotation_items", "quotation_id=?", (qid,))) == 1
