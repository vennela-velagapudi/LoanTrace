from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ingestion import ingest_csv
from app.services.validation import run_validation
from app.models import UploadBatch
import traceback

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        from starlette.concurrency import run_in_threadpool
        
        content = await file.read()
        decoded = content.decode("utf-8")
        filename = file.filename
        
        # Run ingestion in threadpool
        ingest_result = await run_in_threadpool(ingest_csv, db, decoded, filename)
        
        # Run validation in threadpool
        valid_result = await run_in_threadpool(run_validation, db, ingest_result["batch_id"])
        
        return {
            "filename": ingest_result["filename"],
            "source_type": ingest_result["source_type"],
            "total_rows": ingest_result["total_rows"],
            "normalized_count": ingest_result["normalized_count"],
            "failed_count": ingest_result["failed_count"],
            "exceptions_created": valid_result["exceptions_created"],
            "status": "COMPLETED"
        }
    except Exception as e:
        with open("local_error.txt", "w") as f:
            f.write(traceback.format_exc())
        return {"error": str(e), "traceback": traceback.format_exc()}

@router.get("/")
def get_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batches = db.query(UploadBatch).offset(skip).limit(limit).all()
    return batches

@router.get("/latest/summary")
def get_latest_upload_summary(db: Session = Depends(get_db)):
    from app.models import RawRecord, NormalizedLoan, ValidationRun, ExceptionModel, ValidationResult
    batch = db.query(UploadBatch).filter(UploadBatch.status == "COMPLETED").order_by(UploadBatch.uploaded_at.desc()).first()
    if not batch:
        return None
        
    total_rows = db.query(RawRecord).filter(RawRecord.batch_id == batch.id).count()
    
    # Since ingestion dynamically tracks normalized_count and failed_count without saving 
    # to DB, we approximate them here. If needed, the DB schema should be updated later.
    normalized_count = total_rows
    failed_count = 0
    
    val_run = db.query(ValidationRun).filter(ValidationRun.batch_id == batch.id).first()
    exceptions_created = 0
    if val_run:
        exceptions_created = db.query(ExceptionModel)\
            .join(ValidationResult, ExceptionModel.validation_result_id == ValidationResult.id)\
            .filter(ValidationResult.run_id == val_run.id).count()
            
    return {
        "filename": batch.filename,
        "source_type": batch.source_type,
        "total_rows": total_rows,
        "normalized_count": normalized_count,
        "failed_count": failed_count,
        "exceptions_created": exceptions_created,
        "status": batch.status
    }

@router.get("/{batch_id}")
def get_file(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="File/Batch not found")
    return batch
