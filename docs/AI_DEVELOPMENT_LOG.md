# AI Development Log

This document tracks the AI-assisted development process for LoanTrace, explicitly fulfilling the Intain Full Stack Track Agentic Coding Requirement.

## 1. Tools Used
- **Antigravity AI Agent** (Gemini 3.1 Pro High)
- **google-genai** (for backend AI integration)
- **Python / FastAPI**
- **React / Next.js / TypeScript**

## 2. Use Cases
AI tools were used across the entire full-stack lifecycle:
- **Architecture & Schema Design**: Designing the immutable `RawRecord`, `NormalizedLoan`, and `ExceptionModel` schemas.
- **Validation-Rule Generation**: Building the deterministic validation engine and synthetic data generator.
- **API Design & Debugging**: Creating RBAC endpoints, exception handling, and JWT authentication flows.
- **UI Generation**: Rapid scaffolding of the Operator, Reviewer, and Consumer dashboards.
- **Test Generation**: Generating test suites (`pytest`, `jest`) for backend workflows and UI components.
- **Refactoring & Documentation**: Converting mock localStorage authentication to real backend JWT flow, and maintaining the development log.

## 3. Prompt Examples
Here are 9 representative prompts used to drive the agentic development process:
1. *"Initial blueprint generation based on challenge requirements."*
2. *"Corrections to the blueprint (storage abstraction, explicit audit, immutable records) and initiating Phase 1."*
3. *"Initialize Phase 2: Instruct subagents to build the deterministic validation engine, the CSV ingestion pipeline, and the synthetic data generator (~2000 records with 16 intentional corruption types)."*
4. *"Run concurrent execution of data generation script writing and FastAPI backend/DB updates to handle RawRecord, NormalizedLoan, UploadBatch, and ExceptionModel."*
5. *"Implement the Reviewer Workflow, including Exception APIs with RBAC, field editing with dynamic partial revalidation, and append-only Audit Trails."*
6. *"Upgrade the frontend `/login` UI to POST credentials to the backend `/api/auth/token` endpoint and receive a real JWT. Remove the mocked localStorage hardcoded credentials."*
7. *"Explain this loan validation exception to a reviewer mapping JSON context and Pydantic schemas (e.g. AIExplanation) using google-genai."*
8. *"Create SHA-256 deterministic hashing logic for canonical JSON structures. Implement VerifiedLoan APIs and build the ConsumerDashboard to surface audit logs and immutable hashes."*
9. *"Sweep repository for hardcoded localhosts. Fix frontend build configurations and ensure AI mockup logic elegantly degrades without GEMINI_API_KEY."*

## 4. Human Review Process
All AI-generated code is reviewed by the human developer. Tests (`pytest`, `jest`) and build checks are run locally before committing to the main branch. AI-generated architectural decisions (like mutability) were challenged by the human engineer to ensure strict enforcement of the immutable `RawRecord` requirement. Any unsafe, non-deterministic, or hallucinated output was rejected and either manually corrected or re-prompted.

## 5. AI-Generated Code Percentage Estimate
**Overall Estimate:** ~95%
Nearly all of the frontend UI, backend CRUD boilerplate, and test cases were AI-drafted. (100% of the Phase 4 AI Assistant source code was drafted by AI and compiled cleanly).

## 6. What Was Rejected
AI output was rejected and manually fixed in instances where it was inefficient, unsafe, or unsuitable:
1. **SQLAlchemy Mutation Bug**: The AI generated code that updated a `structured_data` JSON SQLAlchemy Column by mutating a dictionary directly. SQLAlchemy did not flag it as modified in the commit, meaning updates failed silently. This unsuitable output was rejected and fixed by assigning a `.copy()` of the dictionary to ensure the DB triggered an update.
2. **Alembic Migration Constraints**: Alembic auto-generate attempted to add a `batch_alter_table` on exceptions that threw SQLite constraint name errors since the exceptions table wasn't actually changing. This unsafe output was rejected and fixed by manually removing the batch alter from the migration script.

## 7. Lessons Learned
- **Where AI helped most**: Rapid scaffolding of repetitive CRUD endpoints, generating Next.js UI component structures for role-based dashboards, writing boilerplate unit tests, and structuring the data ingestion pipeline. Direct Pydantic schema validation inside `google-genai` is incredibly robust and makes tool parsing perfectly deterministic compared to old raw-json text generation.
- **Where human engineering judgment was necessary**: Navigating framework-specific state limitations (like the SQLAlchemy JSON column mutations and SQLite constraints), designing the immutable data architecture (ensuring strict verification blocking on unresolved exceptions), and ensuring proper conversion from mock authentication to real secure JWT routing. SQLAlchemy distinct queries also vary slightly across SQL dialects; human judgment was needed to use `.count()` over subsets safely in SQLite for a lower memory footprint.
