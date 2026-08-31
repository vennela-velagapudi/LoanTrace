from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import AuditLog
import json

router = APIRouter()

@router.get("/exception/{exception_id}")
def get_audit_trail_for_exception(exception_id: int, db: Session = Depends(get_db)):
    """
    Returns chronological events specifically tied to a single exception.
    """
    # Look for logs where entity_id = exception_id and entity_type = "ExceptionModel"
    # OR where entity_type = "NormalizedLoan" and metadata contains triggered_from_exception = exception_id
    
    logs = db.query(AuditLog).filter(
        or_(
            (AuditLog.entity_type == "ExceptionModel") & (AuditLog.entity_id == exception_id),
            (AuditLog.entity_type == "NormalizedLoan") & (AuditLog.metadata_.op("->>")("triggered_from_exception").cast(int) == exception_id)
        )
    ).order_by(AuditLog.timestamp.asc()).all()
    
    return logs

@router.get("/{loan_id}")
def get_audit_trail(loan_id: str, db: Session = Depends(get_db)):
    """
    Returns chronological (oldest first) events for a given loan ID.
    This preserves the natural timeline.
    """
    logs = db.query(AuditLog).filter(AuditLog.loan_id == loan_id).order_by(AuditLog.timestamp.asc()).all()
    return logs
