from pathlib import Path
from app.agent.worker import AutonomousInvoiceWorker
from app.tools.invoice_search import InvoiceSearchTool
from app.tools.billing_system import BillingSystem


def make_worker(tmp_path):
    return AutonomousInvoiceWorker(InvoiceSearchTool("data/invoices"), BillingSystem(str(tmp_path / "billing.db")))


def test_latest_invoice_is_processed(tmp_path):
    result = make_worker(tmp_path).run("Find the latest invoice from Acme Corp and enter it into our billing system")
    assert result["status"] == "completed"
    assert "INV-1042" in result["message"]
    assert result["evidence"]["passed"] is True


def test_duplicate_is_recovered(tmp_path):
    worker = make_worker(tmp_path)
    first = worker.run("Process the latest invoice from Acme Corp")
    second = worker.run("Process the latest invoice from Acme Corp")
    assert first["status"] == "completed"
    assert second["status"] == "completed"
    assert any(x["step"] == "recover" for x in second["trace"])


def test_unknown_vendor_fails_cleanly(tmp_path):
    result = make_worker(tmp_path).run("Process the latest invoice from UnknownCo")
    assert result["status"] == "failed"


def test_missing_vendor_requests_clarification(tmp_path):
    result = make_worker(tmp_path).run("Process the latest invoice")
    assert result["status"] == "needs_clarification"
