# Exception Review Workflow

This document outlines the Phase 3 human exception-review workflow in LoanTrace.

## Exception Lifecycle

1. **OPEN**: Created by the Validation Engine when a rule fails.
2. **IN_REVIEW**: Reviewer is assigned and actively reviewing the exception.
3. **CORRECTION_REQUESTED**: The reviewer requests a correction (data operator fix or external fix required).
4. **RESOLVED**: The reviewer approves the exception (e.g. forced override) OR the reviewer edits an allowed canonical field and the revalidation dynamically marks it resolved.
5. **REJECTED**: The reviewer rejects the loan outright due to the exception.

## State Transitions
- OPEN -> IN_REVIEW (via assign to me)
- IN_REVIEW -> RESOLVED (via approve or edit-fix)
- IN_REVIEW -> REJECTED (via reject)
- IN_REVIEW -> CORRECTION_REQUESTED (via request correction)
- CORRECTION_REQUESTED -> IN_REVIEW (when reviewer resumes work)

## RBAC Permissions
- **DATA_OPERATOR**: Can view queue summary but cannot assign, edit, or approve exceptions.
- **REVIEWER**: Can view queue, assign exceptions, edit allowed fields, add comments, approve, reject, or request correction.
- **DATA_CONSUMER**: Read-only access via audit trail.

## Field Editing & Revalidation
Reviewers can edit canonical fields such as `current_balance`, `interest_rate`, `payment_status`, etc.
When an edit occurs:
1. The new value updates the `NormalizedLoan` record.
2. The `RawRecord` is NEVER modified (preserving original immutable source data).
3. The system dynamically re-runs validation against the modified loan.
4. Any exception tied to this loan that is now fixed by the edit is automatically transitioned to `RESOLVED` with the reason "Resolved via field edit".
5. Unrelated open exceptions are left completely intact.

## Audit Trail Immutability
All actions (assign, edit, comment, approve, reject, revalidation) generate chronological events in the `AuditLog` table.
The system is explicitly designed append-only; there are no `DELETE` or `PUT` endpoints provided to mutate or rewrite audit logs. This guarantees compliance and traceability.

## Concurrency 
An optimistic concurrency mechanism (`version` column) is designed into the `ExceptionModel`. When decisions or assignments are applied, the backend increments the version, preventing race conditions where multiple reviewers might attempt to approve the same exception simultaneously.
