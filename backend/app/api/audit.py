from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from app.database import get_db
from app.models import AuditLog

router = APIRouter()

@router.get("/exception/{exception_id}")
def get_audit_trail_for_exception(exception_id: int, db: Session = Depends(get_db)):
    """
    Returns chronological events specifically tied to a single exception.
    """
    # Use text for JSON extraction to avoid dialect-specific issues or cast issues simply
    logs = db.query(AuditLog).filter(
        or_(
            (AuditLog.entity_type == "ExceptionModel") & (AuditLog.entity_id == exception_id),
            (AuditLog.entity_type == "NormalizedLoan") & (text("CAST(metadata->>'triggered_from_exception' AS INTEGER) = :exc_id"))
        )
    ).params(exc_id=exception_id).order_by(AuditLog.timestamp.asc()).all()
    
    return logs

@router.get("/{loan_id}")
def get_audit_trail(loan_id: str, db: Session = Depends(get_db)):
    """
    Returns chronological (oldest first) events for a given loan ID.
    This preserves the natural timeline.
    """
    logs = db.query(AuditLog).filter(AuditLog.loan_id == loan_id).order_by(AuditLog.timestamp.asc()).all()
    return logs
