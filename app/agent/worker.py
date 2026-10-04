from datetime import datetime
from typing import Dict, List

class AutonomousInvoiceWorker:
    """A deterministic agent loop for a narrow business task.

    The decision policy is explicit and inspectable; an LLM can replace the
    planner later without changing the tool interfaces.
    """
    def __init__(self, search_tool, billing_system):
        self.search = search_tool
        self.billing = billing_system
        self.memory: Dict[str, object] = {}
        self.trace: List[Dict] = []

    def log(self, step: str, detail: str, **extra):
        self.trace.append({"step": step, "detail": detail, **extra})

    def run(self, task: str) -> Dict:
        vendor = self._extract_vendor(task)
        if not vendor:
            return {"status": "needs_clarification", "message": "Please specify the vendor name.", "trace": self.trace}

        self.log("understand", f"Vendor identified as {vendor}")
        self.memory["vendor"] = vendor

        matches = self.search.search(vendor)
        self.log("search", f"Found {len(matches)} matching invoice(s)")
        if not matches:
            return {"status": "failed", "message": f"No invoices found for {vendor}.", "trace": self.trace}

        latest = matches[0]
        self.memory["invoice"] = latest
        self.log("observe", "Selected latest invoice", invoice=latest)

        result = self.billing.create_invoice(latest)
        self.log("execute", "Attempted invoice creation", result=result)

        if not result["success"] and result.get("error") == "DUPLICATE_INVOICE":
            self.log("recover", "Duplicate detected; retrieving existing record")
            result = {**result, "action": None}
        elif not result["success"]:
            return {"status": "failed", "message": "Billing system rejected the invoice.", "trace": self.trace}

        saved = self.billing.get_invoice(latest["invoice_number"])
        verification = self._verify(latest, saved)
        self.log("verify", "Compared source invoice with billing record", verification=verification)

        if not verification["passed"]:
            return {"status": "failed", "message": "Verification failed.", "trace": self.trace}

        return {
            "status": "completed",
            "message": self._summary(latest, result),
            "evidence": verification,
            "trace": self.trace,
        }

    def _verify(self, source, saved):
        if not saved:
            return {"passed": False, "reason": "Record not found after execution."}
        fields = ["invoice_number", "vendor", "amount", "currency", "due_date"]
        mismatches = [f for f in fields if source.get(f) != saved.get(f)]
        return {"passed": not mismatches, "checked": fields, "mismatches": mismatches, "saved_record": saved}

    def _summary(self, invoice, result):
        action = "already existed and was verified" if result.get("action") is None else "was created and verified"
        return (f"Invoice {invoice['invoice_number']} from {invoice['vendor']} "
                f"for {invoice['currency']} {invoice['amount']:,.2f}, due {invoice['due_date']}, "
                f"{action} in the billing system.")

    @staticmethod
    def _extract_vendor(task: str):
        lower = task.lower()
        marker = "from "
        if marker in lower:
            tail = task[lower.index(marker) + len(marker):]
            for stop in [",", " and ", " then ", " enter", " into"]:
                idx = tail.lower().find(stop)
                if idx >= 0:
                    tail = tail[:idx]
            return tail.strip(" .")
        return None
