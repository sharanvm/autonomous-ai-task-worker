import argparse
from app.agent.worker import AutonomousInvoiceWorker
from app.tools.invoice_search import InvoiceSearchTool
from app.tools.billing_system import BillingSystem


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Task Worker prototype")
    parser.add_argument("task", nargs="+", help="Natural-language task")
    parser.add_argument("--db", default="data/billing.db")
    args = parser.parse_args()
    worker = AutonomousInvoiceWorker(InvoiceSearchTool(), BillingSystem(args.db))
    result = worker.run(" ".join(args.task))
    print("\n=== RESULT ===")
    print(result["status"].upper())
    print(result["message"])
    print("\n=== TRACE ===")
    for item in result["trace"]:
        print(f"[{item['step']}] {item['detail']}")
    if result.get("evidence"):
        print("\n=== VERIFICATION ===")
        print(result["evidence"])

if __name__ == "__main__":
    main()
