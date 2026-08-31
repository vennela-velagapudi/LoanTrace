from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import UploadBatch, NormalizedLoan, ExceptionModel, ValidationResult, VerifiedLoan, ValidationRun, ExceptionComment, AIRecommendation

router = APIRouter()



@router.get("/")
def get_summary(db: Session = Depends(get_db)):
    latest_batch = db.query(UploadBatch).filter(UploadBatch.status == "COMPLETED").order_by(UploadBatch.id.desc()).first()
    latest_run = None
    if latest_batch:
        total_loans = db.query(NormalizedLoan).filter(NormalizedLoan.batch_id == latest_batch.id).count()
        latest_run = db.query(ValidationRun).filter(ValidationRun.batch_id == latest_batch.id).order_by(ValidationRun.id.desc()).first()
    else:
        total_loans = 0

    base_query = db.query(ExceptionModel)
    if latest_run:
        base_query = base_query.join(ValidationResult, ExceptionModel.validation_result_id == ValidationResult.id).filter(ValidationResult.run_id == latest_run.id)
    else:
        base_query = base_query.filter(False)
    
    # Exceptions status
    open_exceptions = base_query.filter(ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])).count()
    resolved_exceptions = base_query.filter(ExceptionModel.status == "RESOLVED").count()
    rejected_exceptions = base_query.filter(ExceptionModel.status == "REJECTED").count()
    total_exceptions = open_exceptions + resolved_exceptions + rejected_exceptions

    # Distinct loans with open exceptions
    # In sqlite/postgres, distinct on a specific column might need to be done differently, 
    # but distinct() applies to the selected entity.
    loans_with_open_exceptions = base_query.filter(
        ExceptionModel.status.in_(["OPEN", "IN_REVIEW", "CORRECTION_REQUESTED"])
    ).distinct(ExceptionModel.normalized_loan_id).count()
    
    # Validation results
    if latest_run:
        invalid_loans = db.query(ValidationResult.normalized_loan_id).filter(
            ValidationResult.run_id == latest_run.id,
            ValidationResult.is_valid == False
        ).distinct().count()
    else:
        invalid_loans = 0
        
    valid_loans = total_loans - invalid_loans
    
    total_batches = db.query(UploadBatch).count()
    verified_records = db.query(VerifiedLoan).count()

    # Data Quality Score calculation
    dq_score = 100.0
    if total_loans > 0:
        dq_score = 100.0 * (total_loans - loans_with_open_exceptions) / total_loans

    # Exceptions by severity
    severity_counts = dict(base_query.with_entities(ExceptionModel.severity, func.count(ExceptionModel.id)).group_by(ExceptionModel.severity).all())
    
    # Exceptions by type
    type_counts_raw = base_query.with_entities(ExceptionModel.rule_name, func.count(ExceptionModel.id)).group_by(ExceptionModel.rule_name).all()
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
