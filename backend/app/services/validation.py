import json
import os
from datetime import datetime, date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import NormalizedLoan, RawRecord, ExceptionModel, ValidationRun, ValidationResult

def load_validation_config():
    config_path = os.path.join(os.path.dirname(__file__), "../../../data/validation_rules.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception:
        # Fallback default configuration
        return {
            "required_fields": ["loan_id"],
            "numeric_rules": {
                "principal_min": 0,
                "balance_min": 0
            },
            "interest_rate": {
                "min": 0.0,
                "max": 0.30
            },
            "payment_status": {
                "valid_statuses": ["Current", "Late (16-30 days)", "Late (31-120 days)", "Default", "Charged Off", "Fully Paid", "Closed"],
                "dpd_consistency": {
                    "Current": {"max_dpd": 0},
                    "Fully Paid": {"max_dpd": 0},
                    "Closed": {"max_dpd": 0},
                    "Late (16-30 days)": {"min_dpd": 16, "max_dpd": 30},
                    "Late (31-120 days)": {"min_dpd": 31, "max_dpd": 120}
                }
            },
            "stale_threshold_days": 180,
            "suspicious_borrower_threshold": 3,
            "valid_states": ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'],
            "document_rules": {
                "required_statuses": ["Available", "Pending"]
            }
        }

def run_validation(db: Session, batch_id: int = None):
    import time
    start_t = time.time()
    config = load_validation_config()
    
    run = ValidationRun(batch_id=batch_id)
    db.add(run)
    db.commit()
    db.refresh(run)

    query = db.query(NormalizedLoan)
    if batch_id:
        query = query.filter(NormalizedLoan.batch_id == batch_id)
    
    # Eager load the raw record to avoid N+1
    from sqlalchemy.orm import joinedload
    query = query.options(joinedload(NormalizedLoan.raw_record))
    
    loans = query.all()
    print(f"[Timer] Validation query loans: {time.time() - start_t:.2f}s", flush=True)
    
    # Pre-compute aggregates for duplicate/suspicious checks
    # To check uniqueness globally, we need counts from the entire table
    # But doing this entirely in memory for 8000 rows is okay, though ideally we'd query just what we need.
    all_loans = db.query(NormalizedLoan.loan_id, NormalizedLoan.borrower_id, NormalizedLoan.original_principal, NormalizedLoan.origination_date).all()
    
    print(f"[Timer] Validation query all_loans: {time.time() - start_t:.2f}s", flush=True)
    
    loan_id_counts = {}
    borrower_loan_counts = {}
    borrower_amount_date_counts = {}
    
    for l_id, b_id, p_orig, d_orig in all_loans:
        if l_id:
            loan_id_counts[l_id] = loan_id_counts.get(l_id, 0) + 1
            
        if b_id:
            key_b = f"{b_id}_{d_orig}"
            borrower_loan_counts[key_b] = borrower_loan_counts.get(key_b, 0) + 1
            
            key_dup = f"{b_id}_{p_orig}_{d_orig}"
            borrower_amount_date_counts[key_dup] = borrower_amount_date_counts.get(key_dup, 0) + 1

    loan_ids = [l.id for l in loans]
    
    # Load all existing open exceptions for these loans
    existing_exceptions = db.query(ExceptionModel).filter(
        ExceptionModel.normalized_loan_id.in_(loan_ids),
        ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])
    ).all()
    
    existing_exc_map = {(ex.normalized_loan_id, ex.rule_name): ex for ex in existing_exceptions}

    exceptions = []
    results = []
    active_exc_set = set()

    for loan in loans:
        raw_data = loan.raw_record.row_data if loan.raw_record else {}

        res = ValidationResult(run_id=run.id, normalized_loan_id=loan.id, is_valid=True)
        results.append(res)
        
        def add_exception(rule_name, severity, field, actual, expected, desc):
            res.is_valid = False
            
            existing = existing_exc_map.get((loan.id, rule_name))
            if existing:
                existing.actual_value = str(actual) if actual is not None else None
                existing.expected_condition = str(expected)
                existing.description = desc
                if not hasattr(res, '_existing_exceptions'):
                    res._existing_exceptions = []
                res._existing_exceptions.append(existing)
            else:
                ex = ExceptionModel(
                    normalized_loan_id=loan.id,
                    rule_name=rule_name,
                    severity=severity,
                    field=field,
                    actual_value=str(actual) if actual is not None else None,
                    expected_condition=str(expected),
                    description=desc
                )
                ex.validation_result_id = None
                if not hasattr(res, '_temp_exceptions'):
                    res._temp_exceptions = []
                res._temp_exceptions.append(ex)

        # A. Missing required fields
        for field in config.get("required_fields", []):
            if getattr(loan, field) is None:
                add_exception("missing_required_field", "CRITICAL", field, None, "Present", f"Missing required field: {field}")

        # B. Duplicate loan ID
        if loan.loan_id and loan_id_counts.get(loan.loan_id, 0) > 1:
            add_exception("duplicate_loan_id", "CRITICAL", "loan_id", loan_id_counts.get(loan.loan_id), "1", "Duplicate loan_id in system")

        # J. Duplicate borrower/amount/date
        if loan.borrower_id and loan.original_principal and loan.origination_date:
            key_dup = f"{loan.borrower_id}_{loan.original_principal}_{loan.origination_date}"
            if borrower_amount_date_counts.get(key_dup, 0) > 1:
                add_exception("duplicate_borrower_loan", "HIGH", "borrower_id", key_dup, "unique", "Duplicate borrower + principal + date")

        # J. Suspicious borrower repetition
        if loan.borrower_id:
            key_b = f"{loan.borrower_id}_{loan.origination_date}"
            suspicious_threshold = config.get("suspicious_borrower_threshold", 3)
            if borrower_loan_counts.get(key_b, 0) >= suspicious_threshold:
                add_exception("suspicious_borrower_repetition", "WARNING", "borrower_id", borrower_loan_counts.get(key_b), f"< {suspicious_threshold}", f"Borrower {loan.borrower_id} has {borrower_loan_counts.get(key_b)} loans on the same date")

        # C. Dates
        for date_field in ["origination_date", "maturity_date", "last_payment_date"]:
            raw_val = raw_data.get(date_field)
            if raw_val and getattr(loan, date_field) is None:
                # Value was present in raw but failed parsing
                add_exception("invalid_date_format", "CRITICAL", date_field, raw_val, "YYYY-MM-DD", f"Invalid date format for {date_field}")

        if loan.origination_date and loan.maturity_date:
            if loan.maturity_date <= loan.origination_date:
                add_exception("maturity_before_origination", "CRITICAL", "maturity_date", loan.maturity_date, f"> {loan.origination_date}", "Maturity date is before or equal to origination date")

        # D. Numeric validation
        num_rules = config.get("numeric_rules", {})
        if loan.original_principal is not None and loan.original_principal < num_rules.get("principal_min", 0):
            add_exception("negative_principal", "CRITICAL", "original_principal", loan.original_principal, ">= 0", "Negative original principal")
            
        if loan.current_balance is not None and loan.current_balance < num_rules.get("balance_min", 0):
            add_exception("negative_balance", "CRITICAL", "current_balance", loan.current_balance, ">= 0", "Negative current balance")
            
        if loan.original_principal is not None and loan.current_balance is not None:
            if loan.current_balance > loan.original_principal:
                add_exception("balance_exceeds_principal", "HIGH", "current_balance", loan.current_balance, f"<= {loan.original_principal}", "Current balance exceeds original principal")

        for num_field in ["original_principal", "current_balance"]:
            raw_val = raw_data.get(num_field)
            if raw_val and getattr(loan, num_field) is None:
                add_exception("invalid_numeric_format", "CRITICAL", num_field, raw_val, "numeric", f"Invalid numeric format for {num_field}")

        # E. Interest rate
        ir_rules = config.get("interest_rate", {})
        if loan.interest_rate is not None:
            if loan.interest_rate < ir_rules.get("min", 0.0) or loan.interest_rate > ir_rules.get("max", 0.30):
                add_exception("invalid_interest_rate", "HIGH", "interest_rate", loan.interest_rate, f"{ir_rules.get('min')} - {ir_rules.get('max')}", "Interest rate outside expected range")

        # F. Payment validation
        pay_rules = config.get("payment_status", {})
        valid_statuses = pay_rules.get("valid_statuses", [])
        if loan.payment_status and loan.payment_status not in valid_statuses:
            add_exception("invalid_payment_status", "HIGH", "payment_status", loan.payment_status, "in valid_statuses", "Invalid payment status")
            
        if loan.payment_status and loan.days_past_due is not None:
            consist = pay_rules.get("dpd_consistency", {}).get(loan.payment_status)
            if consist:
                if "max_dpd" in consist and loan.days_past_due > consist["max_dpd"]:
                    add_exception("payment_status_inconsistent_dpd", "CRITICAL", "days_past_due", loan.days_past_due, f"<= {consist['max_dpd']}", f"DPD inconsistent with {loan.payment_status}")
                if "min_dpd" in consist and loan.days_past_due < consist["min_dpd"]:
                    add_exception("payment_status_inconsistent_dpd", "CRITICAL", "days_past_due", loan.days_past_due, f">= {consist['min_dpd']}", f"DPD inconsistent with {loan.payment_status}")

        # K. Closed loans
        if loan.payment_status == "Closed" and loan.current_balance is not None and loan.current_balance > 0:
            add_exception("closed_loan_with_balance", "CRITICAL", "current_balance", loan.current_balance, "0", "Closed loan has positive balance")

        # H. State validation
        if loan.borrower_state and loan.borrower_state not in config.get("valid_states", []):
            add_exception("invalid_state_code", "WARNING", "borrower_state", loan.borrower_state, "valid US state", "Invalid state code")

        # I. Stale records
        stale_threshold = config.get("stale_threshold_days", 180)
        if loan.last_updated_at:
            days_old = (date.today() - loan.last_updated_at).days
            if days_old > stale_threshold:
                add_exception("stale_record", "WARNING", "last_updated_at", loan.last_updated_at, f"< {stale_threshold} days old", "Stale record detected")

        # G. Document validation (Manifest Check)
        doc_req = config.get("document_rules", {}).get("required_statuses", [])
        final_doc_status = loan.manifest_document_status or loan.document_status
        if final_doc_status not in doc_req:
            add_exception("invalid_document_status", "HIGH", "document_status", final_doc_status, f"in {doc_req}", "Document status unavailable or invalid")

        # L. Cross-source conflicts
        conflict_fields = [
            ("current_balance", "servicer_update_current_balance"),
            ("interest_rate", "servicer_update_interest_rate"),
            ("payment_status", "servicer_update_payment_status"),
            ("days_past_due", "servicer_update_days_past_due"),
            ("servicer_name", "servicer_update_servicer_name"),
            ("last_payment_date", "servicer_update_last_payment_date"),
            ("last_updated_at", "servicer_update_last_updated_at"),
            ("document_status", "servicer_update_document_status")
        ]
        
        for tape_field, servicer_field in conflict_fields:
            tape_val = getattr(loan, tape_field, None)
            servicer_val = getattr(loan, servicer_field, None)
            
            if tape_val is not None and servicer_val is not None:
                if tape_val != servicer_val:
                    add_exception(
                        "cross_source_conflict", 
                        "HIGH", 
                        tape_field, 
                        f"Tape: {tape_val} | Servicer: {servicer_val}", 
                        "match", 
                        f"Conflict detected for {tape_field} between loan_tape and servicer_update"
                    )

    print(f"[Timer] Validation processed loop: {time.time() - start_t:.2f}s", flush=True)
    
    try:
        db.add_all(results)
        print(f"[Timer] Validation starting flush: {time.time() - start_t:.2f}s", flush=True)
        db.flush() # Now all res.id are populated
        
        for res in results:
            if hasattr(res, '_existing_exceptions'):
                for ex in res._existing_exceptions:
                    ex.validation_result_id = res.id
                    active_exc_set.add(ex.id)
            if hasattr(res, '_temp_exceptions'):
                for ex in res._temp_exceptions:
                    ex.validation_result_id = res.id
                    exceptions.append(ex)
                    
        # Resolve existing exceptions that were not triggered in this run
        for ex in existing_exceptions:
            if ex.id not in active_exc_set:
                ex.status = "RESOLVED"
                ex.resolved_at = func.now()
                ex.resolution_reason = "Fixed in subsequent validation run"
                    
        if exceptions:
            db.add_all(exceptions)
        
        print(f"[Timer] Validation starting commit: {time.time() - start_t:.2f}s", flush=True)
        db.commit()
        print(f"[Timer] Validation finished commit: {time.time() - start_t:.2f}s", flush=True)
    except Exception as e:
        db.rollback()
        raise e
    
    return {
        "run_id": run.id,
        "loans_processed": len(loans),
        "exceptions_created": len(exceptions)
    }
