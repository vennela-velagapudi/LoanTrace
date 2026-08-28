# AI Development Log

This document tracks the AI-assisted development process for LoanTrace, as required by the challenge.

## Estimated AI-Generated Code Percentage
**Current Estimate:** ~95% (Phase 2 Ingestion & Validation)

## Human Review & Testing Process
All AI-generated code is reviewed by the human developer. Tests (pytest, jest) and build checks are run locally before committing to the main branch. Any unsafe or hallucinated output is rejected and manually corrected or re-prompted.

## Prompts & AI Interactions
### Phase 1: Foundation
*   **Prompt 1**: Initial blueprint generation based on challenge requirements.
*   **Prompt 2**: Corrections to the blueprint (storage abstraction, explicit audit, immutable records) and initiating Phase 1.

### Phase 2: Data Ingestion & Validation
*   **Prompt 3**: Phase 2 initialization. Instructed subagents to build the deterministic validation engine, the CSV ingestion pipeline (preserving raw lineage), and the synthetic data generator (~2000 records with 16 intentional corruption types).
*   **Prompt 4 (Subagents)**: Concurrent execution of data generation script writing and FastAPI backend/DB updates to handle `RawRecord`, `NormalizedLoan`, `UploadBatch`, and `ExceptionModel`.

## Rejected AI Output
*(Examples of rejected output will be added here as they occur)*

## Lessons Learned
*(Lessons will be documented here as development progresses)*

## Phase 3 Development
- **AI Assisted Implementation**: Implemented the Reviewer Workflow, including Exception APIs with RBAC, field editing with dynamic partial revalidation, and append-only Audit Trails. Also built the NextJS /reviewer dashboard.
- **Human Review**: Verified strict enforcement of the immutable RawRecord requirement. Verified that re-running validation handles old unresolved exceptions properly without duplicating or improperly wiping unrelated errors.
- **Tests**: Created test_review.py which fully tests assign, edit, comment, revalidation, and decisions. Tests passed 6/6.
- **Limitations**: The frontend Reviewer authentication is currently mocked using localStorage since true frontend token exchange wasn't strictly enforced in the challenge UI constraints, though the backend enforces JWT properly.

## Phase 3 Hardening
- **Authentication Integration**: Upgraded the frontend /login UI to actually POST credentials to the backend /api/auth/token endpoint and receive a real JWT. Removed the mocked localStorage hardcoded credentials.
- **Frontend RBAC**: Wrote a lib/auth.ts helper and ClientNav.tsx component to handle real token decoding, role enforcement routing (Operator -> /operator, Reviewer -> /reviewer, Consumer -> /consumer), and logout state.
- **Backend RBAC Verification**: Created 	est_auth.py to assert that operators and consumers properly receive 403 Forbidden when attempting reviewer mutations. Handled the passlib compatibility bug with crypt>=4.0.0 gracefully.
- **Full Workflow Intact**: Re-tested validation flows and reviewer APIs.

## Phase 4 AI Review Assistant
- **Tools Used**: AI Agent (myself), Python, FastAPI, google-genai, Next.js, React.
- **Representative Prompts**: Used prompt schemas such as Explain this loan validation exception to a reviewer... mapping JSON context and Pydantic schemas (e.g. AIExplanation).
- **Code Reviewed**: AI Agent reviewed existing DB schemas and wrote new AIRecommendation models.
- **Accepted Changes**: Pydantic structured output models for gemini actions (EXPLAIN, SUGGEST, COMPARE, NOTE, BATCH, RULE). React components for AI Assistant Panel split view.
- **Rejected/Corrected AI Output Examples**: 1. google-genai generates Pydantic models automatically from schema but when structured_data (JSON SQLAlchemy Column) was updated inside a dict directly, SQLAlchemy did not flag it as modified in the commit; fixed by reassigning a .copy() dictionary. 2. Alembic auto-generate attempted to add a atch_alter_table on exceptions that threw SQLite constraint name errors since exceptions table wasn	 changing. Fixed by removing the batch alter from the migration manually.
- **% AI Generated Code**: 100% of the Phase 4 source code was drafted by AI and compiled cleanly.
- **Lessons Learned**: Direct Pydantic schema validation inside google-genai is incredibly robust and makes tool parsing perfectly deterministic compared to old raw-json text generation.

## Phase 5 Verified Records and Consumer Workflow
- **Tools Used**: AI Agent (myself), Python, FastAPI, React.
- **Implementation**: Created SHA-256 deterministic hashing logic for canonical JSON structures. Implemented VerifiedLoan APIs. Built ConsumerDashboard and VerifiedRecordDetail to surface audit logs and immutable hashes.
- **Engineering Decisions**: Made verification explicitly block on unresolved exceptions, matching real-world requirements. Kept export robust by tracking CSV headers dynamically from JSON schemas.
- **Lessons Learned**: SQLAlchemy distinct queries are slightly different across SQL dialects; used .count() over subsets safely in sqlite for memory footprint.

## Phase 6 Final Polish and Security
- **Implementation**: Swept repository for hardcoded localhosts. Fixed frontend build configurations. Ensured AI mockup logic elegantly degrades without GEMINI_API_KEY.
- **Testing**: Re-ran full synthetic data generator to assert massive validation sweeps still process correctly.
