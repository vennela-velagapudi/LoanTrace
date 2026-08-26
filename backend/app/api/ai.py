from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.models import User, ExceptionModel, AIRecommendation
from app.core.security import RoleChecker
from app.services.ai import AIReviewService
from app.services.review import _log_audit

router = APIRouter()
ai_service = AIReviewService()
require_reviewer = RoleChecker(["REVIEWER"])

def build_exception_context(exc: ExceptionModel) -> Dict[str, Any]:
    return {
        "exception_id": exc.id,
        "loan_id": exc.normalized_loan.loan_id if exc.normalized_loan else None,
        "borrower_id": exc.normalized_loan.borrower_id if exc.normalized_loan else None,
        "rule_violated": exc.rule_name,
        "current_severity": exc.severity,
        "field": exc.field,
        "actual_value": exc.actual_value,
        "expected_condition": exc.expected_condition,
        "description": exc.description,
        "raw_record": exc.normalized_loan.raw_record.row_data if exc.normalized_loan and exc.normalized_loan.raw_record else None
    }

def save_recommendation(db: Session, exception_id: int, loan_id: str, user_id: int, action_type: str, raw_response: Any, structured_data: dict, prompt: str, confidence: str = None) -> int:
    rec = AIRecommendation(
        exception_id=exception_id,
        loan_id=loan_id,
        user_id=user_id,
        action_type=action_type,
        model_name=ai_service.model_name,
        prompt_template=prompt,
        structured_data=structured_data,
        raw_response=None,
        confidence=confidence,
        status="GENERATED"
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    
    _log_audit(db, user_id, f"AI_RECOMMENDATION_GENERATED", "AIRecommendation", rec.id, loan_id=loan_id, new_value={"action": action_type})
    
    return rec.id

@router.post("/exceptions/{exception_id}/explain")
def explain_exception(exception_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    context = build_exception_context(exc)
    explanation, prompt = ai_service.explain_exception(context)
    
    rec_id = save_recommendation(
        db, exception_id, exc.normalized_loan.loan_id, current_user.id,
        "EXPLAIN", None, explanation.model_dump(), prompt, explanation.confidence
    )
    
    return {"recommendation_id": rec_id, "data": explanation.model_dump()}

@router.post("/exceptions/{exception_id}/suggest")
def suggest_correction(exception_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    context = build_exception_context(exc)
    suggestion, prompt = ai_service.suggest_correction(context)
    
    rec_id = save_recommendation(
        db, exception_id, exc.normalized_loan.loan_id, current_user.id,
        "SUGGEST", None, suggestion.model_dump(), prompt, suggestion.confidence
    )
    
    return {"recommendation_id": rec_id, "data": suggestion.model_dump()}

@router.post("/exceptions/{exception_id}/compare")
def compare_conflict(exception_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    
    loan = exc.normalized_loan
    if not loan:
        raise HTTPException(status_code=400, detail="No loan associated")
        
    tape_data = loan.raw_record.row_data if loan.raw_record else {}
    servicer_data = {
        "servicer_update_current_balance": loan.servicer_update_current_balance,
        "servicer_update_interest_rate": loan.servicer_update_interest_rate,
        "servicer_update_payment_status": loan.servicer_update_payment_status,
        "servicer_update_days_past_due": loan.servicer_update_days_past_due
    }
        
    context = build_exception_context(exc)
    comparison, prompt = ai_service.compare_conflict(tape_data, servicer_data, context)
    
    rec_id = save_recommendation(
        db, exception_id, loan.loan_id, current_user.id,
        "COMPARE", None, comparison.model_dump(), prompt, comparison.confidence
    )
    
    return {"recommendation_id": rec_id, "data": comparison.model_dump()}

@router.post("/exceptions/{exception_id}/note")
def generate_note(exception_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
        
    context = build_exception_context(exc)
    note, prompt = ai_service.generate_note(context)
    
    rec_id = save_recommendation(
        db, exception_id, exc.normalized_loan.loan_id, current_user.id,
        "NOTE", None, note.model_dump(), prompt, None
    )
    
    return {"recommendation_id": rec_id, "data": note.model_dump()}

class BatchSummaryRequest(BaseModel):
    exception_ids: List[int]

@router.post("/batch-summary")
def batch_summary(req: BatchSummaryRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    exceptions = db.query(ExceptionModel).filter(ExceptionModel.id.in_(req.exception_ids)).all()
    contexts = [build_exception_context(exc) for exc in exceptions]
    
    summary, prompt = ai_service.summarize_batch(contexts)
    
    rec_id = save_recommendation(
        db, None, None, current_user.id,
        "SUMMARY", None, summary.model_dump(), prompt, None
    )
    
    return {"recommendation_id": rec_id, "data": summary.model_dump()}

class RuleRequest(BaseModel):
    natural_language: str

@router.post("/generate-rule")
def generate_rule(req: RuleRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    proposal, prompt = ai_service.generate_rule(req.natural_language)
    
    rec_id = save_recommendation(
        db, None, None, current_user.id,
        "RULE", None, proposal.model_dump(), prompt, None
    )
    
    return {"recommendation_id": rec_id, "data": proposal.model_dump()}

class RecommendationActionRequest(BaseModel):
    action: str # ACCEPT, REJECT, EDIT
    edited_value: Optional[str] = None
    
@router.post("/recommendations/{rec_id}/action")
def act_on_recommendation(rec_id: int, req: RecommendationActionRequest, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    if req.action == "ACCEPT":
        rec.status = "ACCEPTED"
        _log_audit(db, current_user.id, "AI_RECOMMENDATION_ACCEPTED", "AIRecommendation", rec.id, loan_id=rec.loan_id, new_value={"status": "ACCEPTED"})
    elif req.action == "REJECT":
        rec.status = "REJECTED"
        _log_audit(db, current_user.id, "AI_RECOMMENDATION_REJECTED", "AIRecommendation", rec.id, loan_id=rec.loan_id, new_value={"status": "REJECTED"})
    elif req.action == "EDIT":
        rec.status = "EDITED"
        structured = rec.structured_data.copy() if rec.structured_data else {}
        structured["edited_value"] = req.edited_value
        rec.structured_data = structured
        _log_audit(db, current_user.id, "AI_RECOMMENDATION_EDITED", "AIRecommendation", rec.id, loan_id=rec.loan_id, new_value={"status": "EDITED", "edited_value": req.edited_value})
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    db.commit()
    db.refresh(rec)
    return {"status": rec.status}

@router.get("/exceptions/{exception_id}/recommendations")
def get_recommendations(exception_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    recs = db.query(AIRecommendation).filter(AIRecommendation.exception_id == exception_id).order_by(AIRecommendation.id.desc()).all()
    return [{"id": r.id, "action_type": r.action_type, "model_name": r.model_name, "status": r.status, "structured_data": r.structured_data, "confidence": r.confidence, "created_at": r.created_at} for r in recs]
