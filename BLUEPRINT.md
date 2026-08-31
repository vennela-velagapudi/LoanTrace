# LoanTrace: Project Implementation Blueprint

This document outlines the complete architecture, technical stack, and implementation plan for the **LoanTrace** FinTech platform. It acts as the master reference to ensure all challenge requirements are met.

## 1. Recommended Technology Stack

*   **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui. (Delivers a polished, modern FinTech visual identity efficiently).
*   **Backend**: Python 3.12+, FastAPI. (High performance, excellent async support, native Pydantic validation, and industry-standard for AI integrations).
*   **Database**: SQLite. (Relational integrity is crucial for financial data. JSONB support for flexible raw data/audit logs).
*   **ORM**: SQLModel (or SQLAlchemy 2.0). (Seamless integration with FastAPI and Pydantic).
*   **AI Integration**: Google Gemini API (via direct SDK or LangChain). (Used for the AI Review Assistant).
*   **Authentication/Authorization**: Custom JWT-based auth via FastAPI OAuth2. (Simplifies provisioning the exact 3 required test roles without relying on external SaaS limits during the competition).
*   **File Handling**: An abstract FileStorage service. Defaults to local file system for development, with the ability to plug in S3/Supabase Storage for production deployment. S3 is not a mandatory dependency.
*   **Validation**: Pydantic for schema validation + a custom Python-based Rules Engine for business logic.
*   **Testing**: Pytest (Backend), Jest/React Testing Library (Frontend).
*   **Deployment**: Vercel (Frontend), Render or Railway (Backend), Local SQLite.

## 2. Complete System Architecture

The system follows a modern decoupled architecture:

1.  **Presentation Layer (Next.js)**: Handles routing, role-based dashboards (Operator, Reviewer, Consumer), and UI state.
2.  **API Gateway (FastAPI)**: RESTful endpoints routing requests to underlying services.
3.  **Service Layer (Python)**:
    *   `Auth Service`: Manages sessions and role validation.
    *   `Ingestion Service`: Handles CSV parsing, file storage (via abstraction), and initial normalization.
    *   `Validation Engine`: Runs configured rules against normalized data.
    *   `Exception Management Service`: Queues failed records and processes reviewer actions.
    *   `AI Review Service`: Interfaces with the LLM, providing context (loan data, rule failed) and returning structured recommendations.
    *   `Verification Service`: Finalizes approved records, generates cryptographic hashes, and commits to the verified ledger.
    *   `Audit Service`: A cross-cutting dependency explicitly called by business workflows to record actions. (Database events may supplement this, but explicit calls ensure context).
4.  **Data Layer (SQLite + File System/Blob)**: Relational tables for state, JSONB for unstructured data/logs, File Storage abstraction for CSVs.

## 3. Proposed Folder/Repository Structure

```text
LoanTrace/
├── frontend/             # Next.js SPA
├── backend/              # FastAPI Application
├── data/                 # Synthetic datasets & generation scripts
├── docs/                 # Project documentation & Logs
├── scripts/              # DB init, seed scripts
├── docker/               # Docker configurations
├── .gitignore
├── README.md
└── docker-compose.yml    # Local dev environment
```

## 4. Database Schema

Key tables and their purpose. The schema supports all required loan fields.

*   **`users`**: `id`, `username`, `password_hash`, `role`.
*   **`upload_batches`**: `id`, `filename`, `uploaded_by`, `upload_date`, `storage_path`, `status`, `total_rows`, `imported_rows`, `failed_rows`.
*   **`raw_loan_data`**: `id`, `batch_id`, `raw_payload` (JSONB).
*   **`normalized_loans`**: The unified model containing ALL required fields:
    `id`, `batch_id`, `loan_id`, `borrower_id`, `loan_type`, `origination_date`, `maturity_date`, `original_principal`, `current_balance`, `interest_rate`, `term_months`, `borrower_state`, `loan_purpose`, `credit_grade`, `employment_length`, `income_band`, `payment_status`, `days_past_due`, `servicer_name`, `last_payment_date`, `last_updated_at`, `document_status`, `source_system` (and fields to store conflicting data from other sources).
*   **`validation_rules`**: `id`, `field`, `rule_type`, `parameters` (JSONB), `is_active`.
*   **`exceptions`**: `id`, `normalized_loan_id`, `rule_id`, `severity`, `status`.
*   **`verified_loans`**: `id`, `original_loan_id`, `final_data` (JSONB), `verified_by_user_id`, `verification_timestamp`, `record_hash`, `version`. (Verified records are immutable. Corrections create a new version).
*   **`audit_logs`**: `id`, `timestamp`, `user_id`, `action_type`, `entity_type`, `entity_id`, `old_value`, `new_value`, `metadata` (JSONB).

## 5. Complete API Design

*   `/api/auth/token`
*   `/api/ingest/upload`
*   `/api/rules`
*   `/api/exceptions`
*   `/api/ai/analyze-exception/{id}`
*   `/api/verified-loans`
*   `/api/audit/{loan_id}`
*   `/api/health`

## 6. Loan Lifecycle / State Model
1. UPLOADED -> 2. PARSED -> 3. VALIDATING -> (Fail) EXCEPTION_PENDING -> UNDER_REVIEW -> RESOLVED -> VERIFIED. (Pass) -> VERIFIED.
Verified records are immutable snapshots.

## 7. Validation Engine Architecture
The engine separates schema validation from business logic. Configurable via DB.
For conflicting-source validation, the model supports overlapping fields between sources (e.g., `loan_tape_current_balance` vs `servicer_update_current_balance`) so actual conflicting values are displayed and compared.

## 8. Exception and Severity Model
CRITICAL, HIGH, WARNING levels tied to rule failures.

## 9. AI Review Assistant Architecture
Context sent to LLM -> Structured JSON return (reasoning, suggested fields). UI isolates suggestions. AI usage is explicitly audited.

## 10. Audit Trail Architecture
Explicit service-level audit logging. When a Reviewer approves an exception, the `ExceptionService` explicitly creates an `AuditLog` entry before committing the transaction.

## 11. Record Hashing Strategy
SHA-256 hash of the deterministic JSON string of the `VerifiedLoan` final data + user + timestamp.

## 12. Raw-Data / Source-Lineage Strategy
Lineage via Foreign Keys from Verified -> Normalized -> Raw -> Batch.

## 13. Role-Based Access Control (RBAC) Design
Centralized authorization in FastAPI dependencies checking JWT roles (DATA_OPERATOR, REVIEWER, DATA_CONSUMER).

## 14. Dashboard/Page Structure
Dark-first FinTech theme. `operator/`, `reviewer/`, `consumer/` route shells.

## 15. Synthetic Dataset Design
Supports all fields and intentional issues (overlapping conflicts, missing IDs, financial logic errors).

## 16. Deployment Architecture
Render (Backend), Vercel (Frontend), SQLite. Storage abstracted.

## 17. Testing Strategy
Pytest (Backend Unit/API), Jest (Frontend).

## 18. Security Considerations
RBAC, parameterized queries (SQLModel), no exposed secrets, explicit audit trails.

## 19. Documentation Structure
*   `README.md`: Setup, env vars, run instructions.
*   `docs/ARCHITECTURE.md`: Technical deep dive.
*   `docs/VALIDATION_RULES.md`: Living catalog of rules.
*   `docs/AI_DEVELOPMENT_LOG.md`: Required log of prompts, rejections, % generated.
*   `docs/DEMO_SCRIPT.md`: Script for the 5-minute video.

## 20. Milestone Implementation Plan
*   **Phase 1: Foundation**: Repo setup, DB schema, Docker config, Next.js/FastAPI boilerplate, Auth & Roles.
*   **Phase 2: Ingestion & Rules**: CSV parsing, storage abstraction, base Validation Engine.
*   **Phase 3: Review Workflow**: Exception queue, reviewer actions, explicit audit trails.
*   **Phase 4: AI Integration**: LLM integration, AI Copilot UI.
*   **Phase 5: Verification & Consumers**: Record hashing, immutable versions, Verified APIs, Lineage UI.
*   **Phase 6: Deployment & Polish**: Vercel/Render deploy, final CSS polish, documentation.

## 21. Requirements Traceability Matrix

| Req Area | Description | Implementation Target | Phase Status |
| :--- | :--- | :--- | :--- |
| A | Data Ingestion | `backend/services/ingestion.py` | Implemented (Phase 2) |
| B | Validation Engine | `backend/services/validation.py` | Implemented (Phase 2) |
| C | Exception Queue | `backend/api/exceptions.py` | Implemented API Shells (Phase 2) |
| D | AI Review Assistant | `backend/services/ai.py` | Planned (Phase 4) |
| E | Verified Record | `verified_loans` DB table | Implemented Foundation (Phase 1) |
| F | Audit Trail | `audit_logs` DB table, explicit logging | Implemented Foundation (Phase 1) |
| G | Dashboards | Next.js `/operator`, `/reviewer`, `/consumer` | Implemented Upload UI (Phase 2) |
| H | APIs | FastAPI endpoints | Implemented (Phase 2) |
| I | AI Controls | UI separation, audit flag | Planned (Phase 4) |
| J | Tech Requirements | Python, Next.js, SQLite | Implemented (Phase 1) |
| K | Deliverables | GitHub repo, Docs | Implemented Base (Phase 1 & 2) |
| L | Agentic Log | `docs/AI_DEVELOPMENT_LOG.md` | Updated (Phase 2) |

## 22. Ambiguities, Risks & Trade-offs
*   **Storage**: Moved to an abstraction to avoid mandatory S3 dependency.
*   **Audit**: Relying on explicit service calls over DB triggers ensures business context is captured.
*   **Verified Mutability**: Verified records are strictly immutable. Corrections require new versions.

## Phase 6 Deployment & Polish
- Configured Next.js frontend to securely load NEXT_PUBLIC_API_URL instead of hardcoded localhost strings, supporting edge deployment on Vercel.
- Refactored FastAPI backend CORS and config.py to ingest FRONTEND_URL and GEMINI_API_KEY from environment context, supporting PaaS deployment (Render, AWS).
- Completely overhauled README.md and DEMO_SCRIPT.md to reflect a seamless, role-based, end-to-end FinTech presentation.
- Verified full data immutability and append-only ledgers via rigorous code review.
