import csv
import io
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import UploadBatch, RawRecord, NormalizedLoan

def parse_date(val):
    if not val: return None
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_float(val):
    if not val: return None
    try:
        return float(val.replace(',', '').strip())
    except ValueError:
        return None

def parse_int(val):
    if not val: return None
    try:
        return int(val.strip())
    except ValueError:
        return None

def ingest_csv(db: Session, file_content: str, filename: str):
    source_type = "unknown"
    if "loan_tape" in filename.lower():
        source_type = "loan_tape"
    elif "servicer_update" in filename.lower():
        source_type = "servicer_update"
    elif "document_manifest" in filename.lower():
        source_type = "document_manifest"

    batch = UploadBatch(filename=filename, source_type=source_type, status="PROCESSING")
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    reader = csv.DictReader(io.StringIO(file_content))
    total_rows = 0
    normalized_count = 0
    failed_count = 0
    
    for row_idx, row in enumerate(reader):
        total_rows += 1
        loan_id = row.get("loan_id", "").strip()
        
        raw_record = RawRecord(
            batch_id=batch.id,
            row_index=row_idx,
            row_data=row,
            loan_id=loan_id if loan_id else None
        )
        db.add(raw_record)
        db.commit()
        db.refresh(raw_record)
        
        # Determine if we should create or update a NormalizedLoan
        norm = None
        if loan_id:
            norm = db.query(NormalizedLoan).filter(NormalizedLoan.loan_id == loan_id).first()
        
        try:
            if source_type == "loan_tape":
                if not norm:
                    norm = NormalizedLoan(loan_id=loan_id if loan_id else None)
                norm.raw_record_id = raw_record.id
                norm.batch_id = batch.id
                norm.borrower_id = row.get("borrower_id")
                norm.loan_type = row.get("loan_type")
                norm.origination_date = parse_date(row.get("origination_date"))
                norm.maturity_date = parse_date(row.get("maturity_date"))
                norm.original_principal = parse_float(row.get("original_principal"))
                norm.current_balance = parse_float(row.get("current_balance"))
                norm.interest_rate = parse_float(row.get("interest_rate"))
                norm.term_months = parse_int(row.get("term_months"))
                norm.borrower_state = row.get("borrower_state")
                norm.loan_purpose = row.get("loan_purpose")
                norm.credit_grade = row.get("credit_grade")
                norm.employment_length = row.get("employment_length")
                norm.income_band = row.get("income_band")
                norm.payment_status = row.get("payment_status")
                norm.days_past_due = parse_int(row.get("days_past_due"))
                norm.servicer_name = row.get("servicer_name")
                norm.last_payment_date = parse_date(row.get("last_payment_date"))
                norm.last_updated_at = parse_date(row.get("last_updated_at"))
                norm.document_status = row.get("document_status")
                norm.source_system = row.get("source_system")

            elif source_type == "servicer_update":
                if not norm:
                    norm = NormalizedLoan(loan_id=loan_id if loan_id else None)
                norm.servicer_update_current_balance = parse_float(row.get("current_balance"))
                norm.servicer_update_interest_rate = parse_float(row.get("interest_rate"))
                norm.servicer_update_payment_status = row.get("payment_status")
                norm.servicer_update_days_past_due = parse_int(row.get("days_past_due"))
                norm.servicer_update_servicer_name = row.get("servicer_name")
                norm.servicer_update_last_payment_date = parse_date(row.get("last_payment_date"))
                norm.servicer_update_last_updated_at = parse_date(row.get("last_updated_at"))
                norm.servicer_update_document_status = row.get("document_status")

            elif source_type == "document_manifest":
                if not norm:
                    norm = NormalizedLoan(loan_id=loan_id if loan_id else None)
                norm.manifest_document_status = row.get("document_status")
            
            else:
                # If unknown source, just create an empty norm bound to this raw record if possible, or skip
                if not norm:
                    norm = NormalizedLoan(loan_id=loan_id if loan_id else None)
                
            db.add(norm)
            db.commit()
            normalized_count += 1
        except Exception as e:
            db.rollback()
            failed_count += 1

    batch.status = "COMPLETED"
    batch.row_count = total_rows
    batch.failed_count = failed_count
    db.commit()
    
    return {
        "batch_id": batch.id,
        "filename": filename,
        "source_type": source_type,
        "total_rows": total_rows,
        "normalized_count": normalized_count,
        "failed_count": failed_count
    }
