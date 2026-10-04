import sqlite3
from pathlib import Path
from typing import Dict

class BillingSystem:
    def __init__(self, db_path: str = "data/billing.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS invoices (
                invoice_number TEXT PRIMARY KEY,
                vendor TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                due_date TEXT NOT NULL,
                source_file TEXT
            )""")

    def create_invoice(self, invoice: Dict) -> Dict:
        with self._connect() as con:
            try:
                con.execute("INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?)", (
                    invoice["invoice_number"], invoice["vendor"], invoice["amount"],
                    invoice["currency"], invoice["due_date"], invoice.get("source_file", "")
                ))
                return {"success": True, "action": "created", "invoice_number": invoice["invoice_number"]}
            except sqlite3.IntegrityError:
                return {"success": False, "error": "DUPLICATE_INVOICE", "invoice_number": invoice["invoice_number"]}

    def get_invoice(self, invoice_number: str) -> Dict | None:
        with self._connect() as con:
            row = con.execute("SELECT invoice_number,vendor,amount,currency,due_date,source_file FROM invoices WHERE invoice_number=?", (invoice_number,)).fetchone()
        if not row:
            return None
        keys = ["invoice_number", "vendor", "amount", "currency", "due_date", "source_file"]
        return dict(zip(keys, row))
