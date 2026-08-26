from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import UploadBatch, NormalizedLoan, ExceptionModel, ValidationResult, VerifiedLoan

router = APIRouter()

@router.get("/")
def get_summary(db: Session = Depends(get_db)):
    total_loans = db.query(NormalizedLoan).count()
    
    # Exceptions status
    open_exceptions = db.query(ExceptionModel).filter(ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])).count()
    resolved_exceptions = db.query(ExceptionModel).filter(ExceptionModel.status == "RESOLVED").count()
    rejected_exceptions = db.query(ExceptionModel).filter(ExceptionModel.status == "REJECTED").count()
    total_exceptions = open_exceptions + resolved_exceptions + rejected_exceptions

    # Distinct loans with open exceptions
    loans_with_open_exceptions = db.query(ExceptionModel.normalized_loan_id).filter(
        ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])
    ).distinct().count()
    
    # Validation results
    invalid_loans = db.query(ValidationResult.normalized_loan_id).filter(ValidationResult.is_valid == False).distinct().count()
    valid_loans = total_loans - invalid_loans
    
    total_batches = db.query(UploadBatch).count()
    verified_records = db.query(VerifiedLoan).count()

    # Data Quality Score calculation
    # Score = 100 * (Total Loans - Loans with Open Exceptions) / Total Loans
    dq_score = 100.0
    if total_loans > 0:
        dq_score = 100.0 * (total_loans - loans_with_open_exceptions) / total_loans

    # Exceptions by severity
    severity_counts = dict(db.query(ExceptionModel.severity, func.count(ExceptionModel.id)).group_by(ExceptionModel.severity).all())
    
    # Exceptions by type
    type_counts_raw = db.query(ExceptionModel.rule_name, func.count(ExceptionModel.id)).group_by(ExceptionModel.rule_name).all()
    type_counts = {k: v for k, v in type_counts_raw}
    
    # Most common rule
    most_common_rules = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    most_common_rules_list = [k for k, v in most_common_rules]

    return {
        "total_loans": total_loans,
        "valid_loans": valid_loans,
        "invalid_loans": invalid_loans,
        "open_exceptions": open_exceptions,
        "resolved_exceptions": resolved_exceptions,
        "rejected_exceptions": rejected_exceptions,
        "verified_records": verified_records,
        "data_quality_score": round(dq_score, 1),
        "total_validation_failures": total_exceptions,
        "exceptions_by_severity": severity_counts,
        "exceptions_by_type": type_counts,
        "most_common_rules": most_common_rules_list,
        "total_batches": total_batches
    }
