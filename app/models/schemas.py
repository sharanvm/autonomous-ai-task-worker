from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass
class Invoice:
    invoice_number: str
    vendor: str
    amount: float
    currency: str
    due_date: str
    issued_date: str
    source_file: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
