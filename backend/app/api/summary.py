from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import UploadBatch, NormalizedLoan, ExceptionModel, ValidationResult

router = APIRouter()

@router.get("/")
def get_summary(db: Session = Depends(get_db)):
    total_loans = db.query(NormalizedLoan).count()
    
    # Validation results are tied to loans.
    # Get distinct loans that have at least one valid/invalid result
    invalid_loans = db.query(ValidationResult.normalized_loan_id).filter(ValidationResult.is_valid == False).distinct().count()
    valid_loans = total_loans - invalid_loans
    
    total_exceptions = db.query(ExceptionModel).count()
    total_batches = db.query(UploadBatch).count()

    # Exceptions by severity
    severity_counts = dict(db.query(ExceptionModel.severity, func.count(ExceptionModel.id)).group_by(ExceptionModel.severity).all())
    
    # Exceptions by type
    type_counts = dict(db.query(ExceptionModel.rule_name, func.count(ExceptionModel.id)).group_by(ExceptionModel.rule_name).all())

    stale_records = type_counts.get("stale_record", 0)
    duplicate_records = type_counts.get("duplicate_loan_id", 0) + type_counts.get("duplicate_borrower_loan", 0)
    cross_source_conflicts = type_counts.get("cross_source_conflict", 0)

    return {
        "total_loans": total_loans,
        "valid_loans": valid_loans,
        "invalid_loans": invalid_loans,
        "total_validation_failures": total_exceptions,
        "exceptions_by_severity": severity_counts,
        "exceptions_by_type": type_counts,
        "stale_records": stale_records,
        "duplicate_records": duplicate_records,
        "cross_source_conflicts": cross_source_conflicts,
        "total_batches": total_batches
    }
