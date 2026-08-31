# Validation Rules Catalog

This document lists all active validation rules configured in the LoanTrace system.

## Configuration
Rules are evaluated dynamically via `data/validation_rules.json`. The Validation Engine parses this file and enforces the defined parameters against all incoming data.

## Configurable Rules
*   **Missing Required Fields**: Enforces the presence of fields listed in `required_fields` (e.g., `loan_id`).
*   **Numeric Validation**:
    *   **Negative Principal**: Checks that `original_principal` is `>= 0` based on `numeric_rules.principal_min`.
    *   **Negative Balance**: Checks that `current_balance` is `>= 0` based on `numeric_rules.balance_min`.
*   **Interest Rate Bounds**: Ensures `interest_rate` falls within the inclusive `min` and `max` bounds defined in `interest_rate`.
*   **Payment Status & DPD Consistency**:
    *   **Valid Payment Statuses**: Enforces that `payment_status` is one of the strictly allowed strings in `payment_status.valid_statuses`.
    *   **DPD Consistency**: Verifies that `days_past_due` aligns with the current payment status boundaries (e.g., "Current" must have max 0 DPD, "Late (16-30 days)" must have min 16 and max 30 DPD).
*   **Stale Records**: Flags loans where `last_updated_at` is older than `stale_threshold_days`.
*   **Suspicious Borrower Repetition**: Flags borrowers originating multiple loans (>= `suspicious_borrower_threshold`) on the exact same date.
*   **Valid States**: Ensures `borrower_state` matches one of the US state codes configured in `valid_states`.
*   **Document Status**: Validates that `manifest_document_status` or `document_status` is listed in `document_rules.required_statuses`.

## Core Logic Rules (Non-Configurable)
*   **Duplicate Loan ID**: System-wide check ensuring `loan_id` is absolutely unique.
*   **Duplicate Borrower/Principal/Date**: Flags loans with the exact same borrower ID, original principal, and origination date.
*   **Invalid Date/Numeric Format**: Validates data types inherently (ensuring strings successfully parse to standard dates or floats).
*   **Maturity Before Origination**: Verifies that the maturity date strictly follows the origination date.
*   **Balance Exceeds Principal**: Flags loans where the current balance exceeds the original loan amount.
*   **Closed Loan With Balance**: Ensures that a loan marked as "Closed" strictly has a balance of $0.
*   **Cross-Source Conflicts**: The system intrinsically compares duplicate fields provided in the tape versus the servicer update (e.g. `current_balance` vs `servicer_update_current_balance`) and generates exceptions if they mismatch.
