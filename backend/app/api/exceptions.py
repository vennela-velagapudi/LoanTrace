from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ExceptionModel, ExceptionComment, AuditLog, User
from app.core.security import RoleChecker, get_current_user
from pydantic import BaseModel
from typing import Any
from app.services.review import assign_reviewer, add_comment, edit_loan_field, make_decision

router = APIRouter()
require_reviewer = RoleChecker(["REVIEWER"])

class AssignRequest(BaseModel):
    user_id: int

class CommentRequest(BaseModel):
    text: str

class FieldEditRequest(BaseModel):
    field_name: str
    new_value: Any
    reason: str

class DecisionRequest(BaseModel):
    decision: str
    reason: str

@router.get("/")
def get_exceptions(skip: int = 0, limit: int = 100, severity: str = None, rule_name: str = None, status: str = None, assigned_to: int = None, loan_id: str = None, borrower_id: str = None, db: Session = Depends(get_db)):
    query = db.query(ExceptionModel)
    
    from app.models import UploadBatch, ValidationRun, ValidationResult, NormalizedLoan
    latest_batch = db.query(UploadBatch).filter(UploadBatch.status == "COMPLETED").order_by(UploadBatch.id.desc()).first()
    if latest_batch:
        latest_run = db.query(ValidationRun).filter(ValidationRun.batch_id == latest_batch.id).order_by(ValidationRun.id.desc()).first()
        if latest_run:
            query = query.join(ValidationResult, ExceptionModel.validation_result_id == ValidationResult.id).filter(ValidationResult.run_id == latest_run.id)
        else:
            query = query.filter(False)
    else:
        query = query.filter(False)
        
    if loan_id or borrower_id:
        query = query.join(NormalizedLoan, ExceptionModel.normalized_loan_id == NormalizedLoan.id)
        if loan_id:
            query = query.filter(NormalizedLoan.loan_id.ilike(f"%{loan_id}%"))
        if borrower_id:
            query = query.filter(NormalizedLoan.borrower_id.ilike(f"%{borrower_id}%"))
            
    if severity:
        query = query.filter(ExceptionModel.severity == severity)
    if rule_name:
        query = query.filter(ExceptionModel.rule_name == rule_name)
    if status:
        query = query.filter(ExceptionModel.status == status)
    if assigned_to is not None:
        query = query.filter(ExceptionModel.assigned_to == assigned_to)
    return query.order_by(ExceptionModel.id.asc()).offset(skip).limit(limit).all()

@router.get("/{exception_id}")
def get_exception(exception_id: int, db: Session = Depends(get_db)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    comments = db.query(ExceptionComment).filter(ExceptionComment.exception_id == exception_id).all()
    # Eager load the normalized loan and raw record for the UI
    loan = exc.normalized_loan
    raw = loan.raw_record.row_data if loan and loan.raw_record else None
    
    return {
        "exception": exc,
        "loan": loan,
        "raw_source": raw,
        "comments": comments
    }

@router.patch("/{exception_id}/assign")
def api_assign_reviewer(exception_id: int, req: AssignRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    return assign_reviewer(db, exception_id, req.user_id)

@router.post("/{exception_id}/comments")
def api_add_comment(exception_id: int, req: CommentRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    return add_comment(db, exception_id, current_user.id, req.text)

@router.patch("/{exception_id}/fields")
def api_edit_field(exception_id: int, req: FieldEditRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    return edit_loan_field(db, exception_id, current_user.id, req.field_name, req.new_value, req.reason)

@router.post("/{exception_id}/decision")
def api_make_decision(exception_id: int, req: DecisionRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    return make_decision(db, exception_id, current_user.id, req.decision, req.reason)
