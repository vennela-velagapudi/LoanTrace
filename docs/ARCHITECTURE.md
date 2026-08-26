# System Architecture

Please refer to `BLUEPRINT.md` for the complete architectural design of LoanTrace.

## Phase 2 Architecture

### Ingestion & Raw Lineage
The ingestion pipeline is designed to never lose data, even if it is completely malformed.
1. **UploadBatch**: Tracks the uploaded file metadata.
2. **RawRecord**: Stores the exact JSON representation of every CSV row. This layer has no strict type constraints, allowing us to ingest strings into numeric fields without breaking the database.
3. **NormalizedLoan**: A strictly typed schema. If a `RawRecord` fails schema validation (e.g., cannot parse a date), it remains in the raw layer but does not propagate to the normalized layer. This ensures the validation engine can safely run mathematical operations on the normalized data.

### Validation Engine
The validation engine reads rules and applies them against the `NormalizedLoan` table.
* **Deterministic Rules**: Checks for negative balances, maturity > origination, duplicate detection, etc.
* **Cross-Source Checks**: The `NormalizedLoan` model accepts data from both the main tape and the servicer update. The validation engine specifically checks if overlapping fields (like `current_balance` vs `servicer_update_current_balance`) differ, creating an exception if they do.
* **Exceptions**: Failures generate `ExceptionModel` records, which explicitly link back to the `NormalizedLoan` (and subsequently the `RawRecord`), ensuring full auditability of *why* a record failed and *what* the original value was.
