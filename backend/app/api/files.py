from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ingestion import ingest_csv
from app.services.validation import run_validation
from app.models import UploadBatch

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode("utf-8")
    
    # Run ingestion
    ingest_result = ingest_csv(db, decoded, file.filename)
    
    # Run validation immediately after ingestion for this batch
    valid_result = run_validation(db, ingest_result["batch_id"])
    
    return {
        "filename": ingest_result["filename"],
        "source_type": ingest_result.get("source_type", "unknown"),
        "total_rows": ingest_result["total_rows"],
        "normalized_count": ingest_result["normalized_count"],
        "failed_count": ingest_result["failed_count"],
        "exceptions_created": valid_result.get("exceptions_created", 0)
    }

@router.get("/")
def get_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batches = db.query(UploadBatch).offset(skip).limit(limit).all()
    return batches

@router.get("/{batch_id}")
def get_file(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="File/Batch not found")
    return batch
