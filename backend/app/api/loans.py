from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NormalizedLoan

router = APIRouter()

@router.get("/")
def get_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    loans = db.query(NormalizedLoan).offset(skip).limit(limit).all()
    return loans

@router.get("/{loan_id}")
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(NormalizedLoan).filter(NormalizedLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan
