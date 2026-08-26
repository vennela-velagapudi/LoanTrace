from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog

router = APIRouter()

@router.get("/{loan_id}")
def get_audit_trail(loan_id: str, db: Session = Depends(get_db)):
    """
    Returns chronological (oldest first) events for a given loan ID.
    This preserves the natural timeline.
    """
    logs = db.query(AuditLog).filter(AuditLog.loan_id == loan_id).order_by(AuditLog.timestamp.asc()).all()
    return logs
