from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NormalizedLoan

router = APIRouter()

@router.get("/")
def get_loans(skip: int = 0, limit: int = 100, loan_id: str = None, borrower_id: str = None, db: Session = Depends(get_db)):
    query = db.query(NormalizedLoan)
    if loan_id:
        query = query.filter(NormalizedLoan.loan_id.ilike(f"%{loan_id}%"))
    if borrower_id:
        query = query.filter(NormalizedLoan.borrower_id.ilike(f"%{borrower_id}%"))
    loans = query.offset(skip).limit(limit).all()
    return loans

@router.get("/{loan_id}")
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(NormalizedLoan).filter(NormalizedLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan
