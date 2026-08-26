from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ExceptionModel

router = APIRouter()

@router.get("/")
def get_exceptions(skip: int = 0, limit: int = 100, severity: str = None, rule_name: str = None, db: Session = Depends(get_db)):
    query = db.query(ExceptionModel)
    if severity:
        query = query.filter(ExceptionModel.severity == severity)
    if rule_name:
        query = query.filter(ExceptionModel.rule_name == rule_name)
    return query.offset(skip).limit(limit).all()

@router.get("/{exception_id}")
def get_exception(exception_id: int, db: Session = Depends(get_db)):
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    return exc
