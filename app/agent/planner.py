import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class TaskPlanner:
    """Uses an LLM to convert a natural-language task into a safe action plan."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        self.client = OpenAI(api_key=api_key)

    def create_plan(self, task: str) -> dict:
        prompt = f"""
You are the planning component of an autonomous business task worker.

User task:
{task}

Available tools:
1. search_invoices(vendor)
   - Searches the simulated invoice repository.
2. read_invoice(invoice_number)
   - Reads a specific invoice.
3. create_invoice(invoice)
   - Creates the invoice in the simulated billing system.
4. verify_invoice(invoice_number)
   - Verifies the saved billing record.

Create a minimal execution plan.

Rules:
- Identify the user's actual goal.
- Do not invent invoice information.
- Use search_invoices before selecting an invoice.
- Use read_invoice before creating an invoice.
- Always verify after a write operation.
- If required information is missing, return "clarification_required".
- Only use the tools listed above.

Return ONLY valid JSON in this format:

{{
  "status": "ready",
  "goal": "short description",
  "vendor": "vendor name",
  "steps": [
    {{
      "tool": "search_invoices",
      "reason": "why this action is needed"
    }}
  ]
}}

User task:
{task}
"""

        response = self.client.responses.create(
            model="gpt-6-luna",
            input=prompt,
        )

        text = response.output_text.strip()

        return json.loads(text)