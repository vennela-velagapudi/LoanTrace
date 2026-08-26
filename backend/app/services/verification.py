from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import NormalizedLoan, VerifiedLoan, ExceptionModel, AuditLog
from app.core.hashing import generate_record_hash
from app.services.review import _log_audit
from datetime import datetime

def is_loan_eligible_for_verification(db: Session, loan_id: str) -> tuple[bool, str]:
    loan = db.query(NormalizedLoan).filter(NormalizedLoan.loan_id == loan_id).first()
    if not loan:
        return False, "Loan not found"
        
    # Check if there are any blocking exceptions (OPEN, IN_REVIEW, CORRECTION_REQUESTED)
    open_exceptions = db.query(ExceptionModel).filter(
        ExceptionModel.normalized_loan_id == loan.id,
        ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])
    ).count()
    
    if open_exceptions > 0:
        return False, f"Loan has {open_exceptions} unresolved exceptions"
        
    return True, "Eligible"

def build_canonical_data(loan: NormalizedLoan) -> dict:
    return {
        "loan_id": loan.loan_id,
        "borrower_id": loan.borrower_id,
        "loan_type": loan.loan_type,
        "origination_date": loan.origination_date.isoformat() if loan.origination_date else None,
        "maturity_date": loan.maturity_date.isoformat() if loan.maturity_date else None,
        "original_principal": loan.original_principal,
        "current_balance": loan.current_balance,
        "interest_rate": loan.interest_rate,
        "term_months": loan.term_months,
        "borrower_state": loan.borrower_state,
        "loan_purpose": loan.loan_purpose,
        "credit_grade": loan.credit_grade,
        "employment_length": loan.employment_length,
        "income_band": loan.income_band,
        "payment_status": loan.payment_status,
        "days_past_due": loan.days_past_due,
        "servicer_name": loan.servicer_name,
        "last_payment_date": loan.last_payment_date.isoformat() if loan.last_payment_date else None,
        "document_status": loan.manifest_document_status or loan.document_status,
        "source_system": loan.source_system
    }

def verify_loan(db: Session, loan_id: str, user_id: int) -> VerifiedLoan:
    eligible, reason = is_loan_eligible_for_verification(db, loan_id)
    if not eligible:
        raise HTTPException(status_code=400, detail=reason)
        
    loan = db.query(NormalizedLoan).filter(NormalizedLoan.loan_id == loan_id).first()
    
    # Has it already been verified? If so, increment version (we are creating a new immutable version)
    previous_verifications = db.query(VerifiedLoan).filter(VerifiedLoan.original_loan_id == loan.id).order_by(VerifiedLoan.version.desc()).first()
    next_version = (previous_verifications.version + 1) if previous_verifications else 1
    
    canonical_data = build_canonical_data(loan)
    
    # Metadata for verification
    # Get exceptions that were resolved to track reviewer decision lineage
    resolved_exceptions = db.query(ExceptionModel).filter(
        ExceptionModel.normalized_loan_id == loan.id,
        ExceptionModel.status == "RESOLVED"
    ).all()
    
    decisions = [{"exception_id": exc.id, "rule": exc.rule_name, "reason": exc.resolution_reason} for exc in resolved_exceptions]
    
    verification_payload = {
        "canonical_data": canonical_data,
        "loan_id": loan.loan_id,
        "source_batch_id": loan.batch_id,
        "raw_record_id": loan.raw_record_id,
        "reviewer_decisions": decisions,
        "verification_timestamp": datetime.utcnow().isoformat(),
        "verified_by_user_id": user_id,
        "version": next_version
    }
    
    # Hash the canonical payload
    record_hash = generate_record_hash(verification_payload)
    verification_payload["record_hash"] = record_hash
    
    verified_loan = VerifiedLoan(
        original_loan_id=loan.id,
        verified_data=verification_payload,
        verified_by_user_id=user_id,
        record_hash=record_hash,
        version=next_version
    )
    db.add(verified_loan)
    
    _log_audit(
        db=db, 
        user_id=user_id, 
        action="LOAN_VERIFIED", 
        entity_type="VerifiedLoan", 
        entity_id=None, # Will update after flush
        loan_id=loan.loan_id, 
        new_value={"version": next_version, "record_hash": record_hash}
    )
    
    db.commit()
    db.refresh(verified_loan)
    
    # Update audit log with new entity id
    latest_audit = db.query(AuditLog).filter(AuditLog.action == "LOAN_VERIFIED", AuditLog.loan_id == loan.loan_id).order_by(AuditLog.id.desc()).first()
    if latest_audit:
        latest_audit.entity_id = verified_loan.id
        db.commit()
        
    return verified_loan
