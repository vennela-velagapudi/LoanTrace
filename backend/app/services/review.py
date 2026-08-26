from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import ExceptionModel, ExceptionComment, AuditLog, NormalizedLoan, ValidationResult, RawRecord
from datetime import datetime, date
import os
import json

EDITABLE_FIELDS = [
    "current_balance",
    "interest_rate",
    "payment_status",
    "days_past_due",
    "servicer_name",
    "document_status",
    "borrower_state",
    "last_payment_date"
]

def load_validation_config():
    config_path = os.path.join(os.path.dirname(__file__), "../../../data/validation_rules.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception:
        return {} # Should not happen in this phase

def _log_audit(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, loan_id: str = None, old_value=None, new_value=None, metadata=None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        loan_id=loan_id,
        old_value=old_value,
        new_value=new_value,
        metadata_=metadata
    )
    db.add(log)
    db.flush()

def get_exception_or_404(db: Session, exception_id: int):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    return exc

def assign_reviewer(db: Session, exception_id: int, user_id: int):
    exc = get_exception_or_404(db, exception_id)
    old_status = exc.status
    old_assigned = exc.assigned_to

    if exc.version:
        exc.version += 1

    exc.assigned_to = user_id
    if exc.status == "OPEN":
        exc.status = "IN_REVIEW"

    _log_audit(db, user_id, "REVIEWER_ASSIGNED", "ExceptionModel", exc.id, 
               loan_id=exc.normalized_loan.loan_id if exc.normalized_loan else None,
               old_value={"assigned_to": old_assigned, "status": old_status},
               new_value={"assigned_to": user_id, "status": exc.status})
    db.commit()
    db.refresh(exc)
    return exc

def add_comment(db: Session, exception_id: int, user_id: int, text: str):
    exc = get_exception_or_404(db, exception_id)
    comment = ExceptionComment(
        exception_id=exception_id,
        reviewer_id=user_id,
        comment_text=text
    )
    db.add(comment)
    _log_audit(db, user_id, "REVIEW_COMMENT_ADDED", "ExceptionModel", exc.id,
               loan_id=exc.normalized_loan.loan_id if exc.normalized_loan else None,
               new_value={"comment": text})
    db.commit()
    db.refresh(comment)
    return comment

def edit_loan_field(db: Session, exception_id: int, user_id: int, field_name: str, new_value: any, reason: str):
    if field_name not in EDITABLE_FIELDS:
        raise HTTPException(status_code=400, detail=f"Field {field_name} is not editable")
    
    exc = get_exception_or_404(db, exception_id)
    loan = exc.normalized_loan
    if not loan:
        raise HTTPException(status_code=400, detail="No normalized loan attached to this exception")
    
    old_val = getattr(loan, field_name)
    setattr(loan, field_name, new_value)
    
    _log_audit(db, user_id, "FIELD_EDITED", "NormalizedLoan", loan.id,
               loan_id=loan.loan_id,
               old_value={field_name: old_val},
               new_value={field_name: new_value},
               metadata={"reason": reason, "triggered_from_exception": exception_id})
    
    db.commit()
    
    # Revalidation logic
    revalidate_loan(db, loan, user_id)
    
    db.refresh(exc)
    return exc

def revalidate_loan(db: Session, loan: NormalizedLoan, user_id: int):
    """
    Reruns validation on a single loan, keeping unresolved exceptions open and resolving fixed ones.
    """
    config = load_validation_config()
    raw = db.query(RawRecord).filter(RawRecord.id == loan.raw_record_id).first() if loan.raw_record_id else None
    raw_data = raw.row_data if raw else {}

    current_exceptions = db.query(ExceptionModel).filter(
        ExceptionModel.normalized_loan_id == loan.id,
        ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])
    ).all()
    
    # Run the rules virtually
    new_violations = set()
    
    # We replicate the rules to determine what is currently failing for this loan
    # (Excluding duplicate tracking which is batch level, and stale/suspicious which are batch level)
    
    # D. Numeric rules
    num_rules = config.get("numeric_rules", {})
    if loan.original_principal is not None and loan.original_principal < num_rules.get("principal_min", 0):
        new_violations.add("negative_principal")
    if loan.current_balance is not None and loan.current_balance < num_rules.get("balance_min", 0):
        new_violations.add("negative_balance")
    if loan.original_principal is not None and loan.current_balance is not None and loan.current_balance > loan.original_principal:
        new_violations.add("balance_exceeds_principal")
        
    # E. Interest rate
    ir_rules = config.get("interest_rate", {})
    if loan.interest_rate is not None and (loan.interest_rate < ir_rules.get("min", 0.0) or loan.interest_rate > ir_rules.get("max", 0.30)):
        new_violations.add("invalid_interest_rate")
        
    # F. Payment validation
    pay_rules = config.get("payment_status", {})
    valid_statuses = pay_rules.get("valid_statuses", [])
    if loan.payment_status and loan.payment_status not in valid_statuses:
        new_violations.add("invalid_payment_status")
    if loan.payment_status and loan.days_past_due is not None:
        consist = pay_rules.get("dpd_consistency", {}).get(loan.payment_status)
        if consist:
            if "max_dpd" in consist and loan.days_past_due > consist["max_dpd"]:
                new_violations.add("payment_status_inconsistent_dpd")
            if "min_dpd" in consist and loan.days_past_due < consist["min_dpd"]:
                new_violations.add("payment_status_inconsistent_dpd")

    # K. Closed loans
    if loan.payment_status == "Closed" and loan.current_balance is not None and loan.current_balance > 0:
        new_violations.add("closed_loan_with_balance")

    # H. State validation
    if loan.borrower_state and loan.borrower_state not in config.get("valid_states", []):
        new_violations.add("invalid_state_code")
        
    # G. Document validation
    doc_req = config.get("document_rules", {}).get("required_statuses", [])
    final_doc_status = loan.manifest_document_status or loan.document_status
    if final_doc_status not in doc_req:
        new_violations.add("invalid_document_status")

    # Now, compare old exceptions to new violations
    for exc in current_exceptions:
        if exc.rule_name in ["negative_principal", "negative_balance", "balance_exceeds_principal", 
                             "invalid_interest_rate", "invalid_payment_status", "payment_status_inconsistent_dpd",
                             "closed_loan_with_balance", "invalid_state_code", "invalid_document_status"]:
            if exc.rule_name not in new_violations:
                # The exception was fixed by the edit!
                exc.status = "RESOLVED"
                exc.resolved_at = datetime.utcnow()
                exc.resolution_reason = "Resolved via field edit"
                if exc.version: exc.version += 1
                
                _log_audit(db, user_id, "VALIDATION_RERUN_RESOLVED", "ExceptionModel", exc.id,
                           loan_id=loan.loan_id,
                           new_value={"status": "RESOLVED"})
                           
    db.commit()


def make_decision(db: Session, exception_id: int, user_id: int, decision: str, reason: str):
    exc = get_exception_or_404(db, exception_id)
    
    valid_decisions = ["APPROVE", "REJECT", "REQUEST_CORRECTION"]
    if decision not in valid_decisions:
        raise HTTPException(status_code=400, detail="Invalid decision")

    if exc.version:
        exc.version += 1

    old_status = exc.status
    if decision == "APPROVE":
        exc.status = "RESOLVED"
    elif decision == "REJECT":
        exc.status = "REJECTED"
    elif decision == "REQUEST_CORRECTION":
        exc.status = "CORRECTION_REQUESTED"

    exc.resolved_at = datetime.utcnow()
    exc.resolution_reason = reason
    
    _log_audit(db, user_id, f"EXCEPTION_{decision}", "ExceptionModel", exc.id,
               loan_id=exc.normalized_loan.loan_id if exc.normalized_loan else None,
               old_value={"status": old_status},
               new_value={"status": exc.status, "reason": reason})
               
    db.commit()
    db.refresh(exc)
    return exc
