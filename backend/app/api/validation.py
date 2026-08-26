from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.validation import run_validation as execute_validation
from app.models import ValidationRun
from pydantic import BaseModel

router = APIRouter()

class ValidationRunRequest(BaseModel):
    batch_id: int = None

@router.post("/run")
def run_validation_endpoint(req: ValidationRunRequest = None, db: Session = Depends(get_db)):
    batch_id = req.batch_id if req else None
    result = execute_validation(db, batch_id)
    return result

@router.get("/runs")
def get_validation_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(ValidationRun).offset(skip).limit(limit).all()
    return runs

@router.get("/runs/{run_id}")
def get_validation_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
