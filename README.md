# Autonomous AI Task Worker

A narrow prototype of an autonomous business task worker. It accepts a natural-language invoice-processing request, searches a simulated invoice repository, selects the latest invoice, writes it to a simulated billing system, handles duplicate records, verifies the final state, and returns evidence.

## Why this scope

The assignment values genuine autonomous execution over breadth. This prototype deliberately uses a small simulated environment so the execution, recovery, and verification loop is real and testable.

## Architecture

`Natural language task -> worker -> tools -> observe -> recover if needed -> verify -> concise result`

### Components

- `app/agent/worker.py`: orchestration loop, memory, decision policy, recovery and verification.
- `app/tools/invoice_search.py`: searches/reads simulated invoice files.
- `app/tools/billing_system.py`: SQLite-backed simulated company billing application.
- `app/models/schemas.py`: domain model.
- `data/invoices/`: sample business documents.
- `tests/`: automated behavior tests.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main "Find the latest invoice from Acme Corp and enter it into our billing system"
```

The worker will:

1. Identify the vendor from the request.
2. Search all matching invoices.
3. Select the newest issued invoice.
4. Attempt to create the billing record.
5. Detect a duplicate if the record already exists.
6. Retrieve the existing record when appropriate.
7. Compare the source and destination fields.
8. Return a completion summary and execution trace.

## Tests

```bash
pytest -q
```

Expected result: 4 tests passing.

## Failure handling

The billing database intentionally enforces a unique invoice number. Running the same task twice causes the second create operation to return a duplicate error. The worker treats that as a recoverable state, retrieves the existing record, and verifies it instead of blindly retrying the same action.

## Verification

Success is not inferred from the create call. The worker performs a separate read-back and compares invoice number, vendor, amount, currency, and due date. Any mismatch causes the task to fail verification.

## AI/model decision

The core prototype uses an explicit, inspectable decision policy so the behavior is deterministic and easy to test. This is intentional: an LLM should be introduced at the task-understanding/planning boundary, while deterministic business tools and verification remain constrained. A future version can replace `_extract_vendor()` with an LLM structured-output planner without changing the tool interfaces.

## Assumptions

- Invoice documents are represented as JSON for the prototype.
- The latest invoice means the highest `issued_date` among matching invoices.
- The vendor name is present in the user's request.
- The simulated billing application is authoritative for saved-state verification.
- No real company credentials or third-party systems are used.

## Known limitations

- Vendor extraction is intentionally narrow and rule-based.
- The prototype does not yet operate an arbitrary browser or desktop UI.
- Only invoice processing is supported.
- No human approval workflow is implemented for high-risk actions.
- The current recovery policy handles duplicate records, not every possible business error.

## What I would build next

1. Add an LLM structured planner with typed tool calls.
2. Add a browser tool against a local simulated web application.
3. Add explicit approval gates for financial/high-impact actions.
4. Add richer retry policies with bounded attempts and error classification.
5. Add persistent task state so interrupted jobs can resume.
6. Add evaluation datasets covering ambiguous requests, failures, and conflicting source data.
7. Add a small UI showing plan, actions, observations, verification, and evidence.

## Demo scenario

Use:

`Find the latest invoice from Acme Corp and enter it into our billing system`

Run it once to show creation and verification. Run the same command again to demonstrate duplicate detection, recovery, and verification of the existing record.
