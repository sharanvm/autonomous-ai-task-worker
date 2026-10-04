import json
from pathlib import Path
from typing import List, Dict

class InvoiceSearchTool:
    def __init__(self, directory: str = "data/invoices"):
        self.directory = Path(directory)

    def search(self, vendor: str) -> List[Dict]:
        results = []
        for path in self.directory.glob("*.json"):
            data = json.loads(path.read_text())
            if vendor.lower() in data["vendor"].lower():
                results.append({**data, "source_file": str(path)})
        results.sort(key=lambda x: x["issued_date"], reverse=True)
        return results

    def read(self, source_file: str) -> Dict:
        return json.loads(Path(source_file).read_text())
