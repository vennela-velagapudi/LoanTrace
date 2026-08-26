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
