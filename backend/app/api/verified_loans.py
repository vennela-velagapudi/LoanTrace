from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.models import User, VerifiedLoan, AuditLog
from app.core.security import RoleChecker, get_current_user
from app.services.verification import verify_loan
from app.services.review import _log_audit

router = APIRouter()

require_reviewer = RoleChecker(["REVIEWER"])
# Consumer or Reviewer can access verified loans
def require_consumer_or_reviewer(user: User = Depends(get_current_user)):
    if user.role not in ["DATA_CONSUMER", "REVIEWER"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

@router.post("/verify/{loan_id}")
def verify_loan_endpoint(loan_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_reviewer)):
    v_loan = verify_loan(db, loan_id, current_user.id)
    return {"status": "success", "verified_loan_id": v_loan.id, "hash": v_loan.record_hash}

@router.get("/")
def get_verified_loans(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_consumer_or_reviewer)
):
    # Only return the most recent version of each verified loan by joining or group by, 
    # but for simplicity since versioning is linear, we can just return all or distinct
    # Actually, let's just return all verified records, ordered by latest.
    records = db.query(VerifiedLoan).order_by(VerifiedLoan.verification_timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "loan_id": r.verified_data.get("loan_id"),
            "verification_timestamp": r.verification_timestamp,
            "verified_by": r.verified_by_user_id,
            "record_hash": r.record_hash,
            "version": r.version,
            "canonical_data": r.verified_data.get("canonical_data")
        } for r in records
    ]

@router.get("/export")
def export_verified_loans(db: Session = Depends(get_db), current_user: User = Depends(require_consumer_or_reviewer)):
    records = db.query(VerifiedLoan).order_by(VerifiedLoan.verification_timestamp.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    if not records:
        return StreamingResponse(iter(["verification_id,record_hash,verification_timestamp,version\n"]), media_type="text/csv")
        
    # Write header
    first_canonical = records[0].verified_data.get("canonical_data", {})
    headers = ["verification_id", "record_hash", "verification_timestamp", "version"] + list(first_canonical.keys())
    writer.writerow(headers)
    
    for r in records:
        canonical = r.verified_data.get("canonical_data", {})
        row = [
            r.id,
            r.record_hash,
            r.verification_timestamp.isoformat() if r.verification_timestamp else "",
            r.version
        ]
        row.extend([canonical.get(k, "") for k in first_canonical.keys()])
        writer.writerow(row)
        
    _log_audit(db, current_user.id, "VERIFIED_RECORDS_EXPORTED", "VerifiedLoan", 0, metadata={"record_count": len(records)})
    db.commit()
    
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=verified_loans.csv"
    return response

@router.get("/{id}")
def get_verified_loan_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(require_consumer_or_reviewer)):
    r = db.query(VerifiedLoan).filter(VerifiedLoan.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Verified record not found")
        
    _log_audit(db, current_user.id, "VERIFIED_RECORD_VIEWED", "VerifiedLoan", r.id, loan_id=r.verified_data.get("loan_id"))
    db.commit()
    
    return {
        "id": r.id,
        "verified_data": r.verified_data,
        "verification_timestamp": r.verification_timestamp,
        "verified_by": r.verified_by_user_id,
        "record_hash": r.record_hash,
        "version": r.version
    }
