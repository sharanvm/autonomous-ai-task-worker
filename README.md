# Autonomous AI Task Worker

A narrow, working prototype of an autonomous business task worker that accepts a natural-language request, determines the required actions, executes them using business tools, handles a recoverable failure, verifies the final state, and returns concise evidence of completion.

## Problem

Business users often need to perform repetitive workflows across documents and internal applications.

For example:

> “Find the latest invoice from Acme Corp and enter it into our billing system.”

A useful task worker should not require the user to specify every individual step. It should understand the objective, perform the necessary actions, react to the results, recover from reasonable failures, and verify that the requested outcome was actually achieved.

## Prototype Scope

This prototype focuses on one complete workflow:

**Invoice Processing**

The worker can:

1. Accept a natural-language task.
2. Identify the requested vendor.
3. Search a simulated invoice repository.
4. Select the latest matching invoice.
5. Read the invoice data.
6. Create a record in a simulated billing application.
7. Detect duplicate-record failures.
8. Recover by retrieving the existing record.
9. Verify the saved record against the source invoice.
10. Return a concise result and execution trace.

The environment is intentionally simulated so that the workflow can be executed safely and repeatedly without real company credentials or third-party systems.

---

## Architecture

```text
                  Natural Language Task
                           |
                           v
                  +-------------------+
                  |   Task Worker     |
                  |                   |
                  | Understand Goal   |
                  | Select Actions    |
                  | Maintain State    |
                  | Recover Errors    |
                  +---------+---------+
                            |
                            v
                    +---------------+
                    | Tool Layer    |
                    +-------+-------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
      Invoice Repository          Billing Application
              |                           |
              +-------------+-------------+
                            |
                            v
                       Observation
                            |
                            v
                    +---------------+
                    | Verification  |
                    +-------+-------+
                            |
                            v
                  Result + Evidence
```

### Main Components

| Component | Purpose |
|---|---|
| `app/agent/worker.py` | Main task orchestration, decision policy, recovery and verification |
| `app/tools/invoice_search.py` | Searches and reads simulated invoice documents |
| `app/tools/billing_system.py` | SQLite-backed simulated billing application |
| `app/models/schemas.py` | Structured invoice/domain models |
| `app/main.py` | Command-line entry point |
| `data/invoices/` | Sample invoice documents |
| `tests/` | Automated tests |

---

## Execution Flow

For the example task:

```text
Find the latest invoice from Acme Corp and enter it into our billing system.
```

the worker performs:

```text
1. Understand request
        ↓
2. Identify vendor
        ↓
3. Search invoice repository
        ↓
4. Select latest invoice
        ↓
5. Attempt billing-system write
        ↓
6. Observe result
        ↓
7. Recover if duplicate exists
        ↓
8. Read saved record
        ↓
9. Compare source vs destination
        ↓
10. Return result and evidence
```

This follows an **act → observe → recover → verify** approach rather than assuming that an action succeeded simply because it was attempted.

---

## Reliability and Failure Handling

The simulated billing application enforces a unique invoice number.

Therefore, running the same task more than once can produce:

```text
Duplicate invoice number
```

The worker does not blindly repeat the same operation.

Instead, it:

1. Detects that the invoice already exists.
2. Treats the duplicate as a recoverable state.
3. Retrieves the existing billing record.
4. Compares it with the source invoice.
5. Completes the task only if verification succeeds.

This demonstrates a basic recovery strategy for unexpected execution states.

---

## Verification

Verification is an independent step after execution.

The worker compares:

- Invoice number
- Vendor
- Amount
- Currency
- Due date

Example successful verification:

```text
passed: True

checked:
- invoice_number
- vendor
- amount
- currency
- due_date

mismatches: []
```

The worker therefore does not consider the task complete merely because the database write returned successfully.

---

## Example Result

```text
=== RESULT ===
COMPLETED

Invoice INV-1042 from Acme Corp for INR 48,500.00,
due 2026-10-20, was created and verified in the billing system.
```

Execution trace:

```text
[understand] Vendor identified as Acme Corp
[search] Found 2 matching invoice(s)
[observe] Selected latest invoice
[execute] Attempted invoice creation
[verify] Compared source invoice with billing record
```

---

## Technology Stack

- Python
- SQLite
- Pydantic
- Pytest
- JSON-based simulated business documents

No real company credentials or unauthorized third-party systems are used.

---

## Setup

### Requirements

Python 3.10+ recommended.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run the Worker

```bash
python -m app.main "Find the latest invoice from Acme Corp and enter it into our billing system"
```

---

## Run Tests

```bash
pytest
```

Expected result:

```text
4 passed
```

---

## Design Decisions

### 1. Narrow scope instead of broad simulation

The assignment prioritizes a narrow prototype that genuinely works over a large system with mocked functionality.

Therefore, this implementation focuses on one complete business workflow rather than attempting to support arbitrary websites and desktop applications.

### 2. Deterministic business tools

The invoice repository and billing system use deterministic interfaces.

This makes the actual business operations:

- Testable
- Reproducible
- Safe
- Easy to debug

An AI planning layer can be added above these tools without allowing an unrestricted model to directly modify the database.

### 3. Separate execution from verification

The worker treats verification as a separate operation.

This reduces the risk of reporting success when the requested state was not actually achieved.

### 4. Bounded recovery

Only known, recoverable failures are automatically handled.

For example, a duplicate invoice can be safely investigated and verified.

Unknown or potentially destructive failures should instead require additional handling or human approval.

---

## Assumptions

- Invoice documents are represented as JSON in the prototype.
- The latest invoice is determined using the invoice `issued_date`.
- The vendor is present in the natural-language request.
- The simulated billing database represents the destination system.
- Invoice numbers are unique in the billing system.
- No real financial transaction is performed.
- Sample data is synthetic and contains no confidential company information.

---

## Known Limitations

This is a prototype and intentionally has a limited scope.

- Vendor extraction is currently narrow and rule-based.
- Only invoice-processing tasks are supported.
- The prototype does not control arbitrary websites or desktop applications.
- The business environment is simulated.
- Recovery currently focuses on duplicate invoice records.
- There is no persistent long-running job queue.
- Human approval gates are not yet implemented.
- The prototype does not attempt unrestricted autonomous actions against external systems.

---

## What I Would Build Next

If additional development time were available, the next improvements would be:

### 1. LLM-based task planning

Introduce a structured-output LLM planner that converts arbitrary natural-language requests into typed tool calls.

```text
User Goal
   ↓
LLM Planner
   ↓
Structured Action
   ↓
Tool
   ↓
Observation
   ↓
LLM Decision
   ↓
Next Action / Recovery
```

The existing deterministic tools and verification layer would remain unchanged.

### 2. Browser-based execution

Add a browser tool against a local simulated company application to demonstrate interaction with a graphical interface.

### 3. Human approval

Add approval gates before high-impact actions such as financial submissions or irreversible changes.

### 4. Better error classification

Introduce bounded retry policies and classify errors into:

- Retryable
- Recoverable
- Requires clarification
- Requires human approval
- Terminal failure

### 5. Persistent task state

Store task state so an interrupted workflow can resume instead of starting from the beginning.

### 6. Evaluation framework

Create a benchmark containing:

- Successful tasks
- Missing information
- Duplicate records
- Invalid invoices
- Conflicting data
- Tool failures
- Ambiguous user requests

This would allow the worker's autonomy and reliability to be measured systematically.

---

## Demo Scenario

Use the following task during the demonstration:

```text
Find the latest invoice from Acme Corp and enter it into our billing system.
```

### Demonstration 1 — Successful execution

Run:

```bash
python -m app.main "Find the latest invoice from Acme Corp and enter it into our billing system"
```

Show:

- Invoice search
- Latest invoice selection
- Billing-system execution
- Verification
- `COMPLETED`
- `passed: True`

### Demonstration 2 — Recovery

Run the same command again.

The billing system will detect the duplicate invoice number.

The worker will:

```text
Detect duplicate
      ↓
Retrieve existing record
      ↓
Compare with source
      ↓
Verify
      ↓
Complete
```

This demonstrates that the worker can react to an unexpected state instead of blindly repeating the failed action.

---

## Submission Summary

This prototype demonstrates the core concepts requested in the assignment:

- **Autonomy:** determines the required invoice-processing steps from a natural-language goal.
- **Execution:** performs actual operations against a simulated business system.
- **Reliability:** handles a duplicate-record failure.
- **Verification:** independently confirms the resulting state.
- **Generalization:** accepts natural-language task descriptions within the supported workflow.
- **Engineering Quality:** uses modular tools, structured models, SQLite and automated tests.
- **Product Thinking:** focuses on completing the user's objective and providing evidence rather than simply explaining what should be done.

The prototype intentionally prioritizes a small, reliable, demonstrable workflow over unsupported breadth.