import io
import csv
import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import update
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
        return float(val.replace(",", "").strip())
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
    
    start_t = time.time()
    
    reader = csv.DictReader(io.StringIO(file_content))
    rows = list(reader)
    total_rows = len(rows)
    normalized_count = 0
    failed_count = 0
    
    print(f"[Timer] Read CSV: {time.time() - start_t:.2f}s", flush=True)
    
    # 1. Insert RawRecords first so they get IDs
    raw_records = []
    for row_idx, row in enumerate(rows):
        loan_id = row.get("loan_id", "").strip()
        raw_records.append(RawRecord(
            batch_id=batch.id,
            row_index=row_idx,
            row_data=row,
            loan_id=loan_id if loan_id else None
        ))
    db.add_all(raw_records)
    db.flush()
    print(f"[Timer] Flushed RawRecords: {time.time() - start_t:.2f}s", flush=True)

    # 2. Query existing NormalizedLoans
    loan_ids = [row.get("loan_id", "").strip() for row in rows if row.get("loan_id", "").strip()]
    existing_norms_list = db.query(NormalizedLoan).filter(NormalizedLoan.loan_id.in_(loan_ids)).all() if loan_ids else []
    existing_norms = {norm.loan_id: norm for norm in existing_norms_list if norm.loan_id}
    
    print(f"[Timer] Query existing NormalizedLoans: {time.time() - start_t:.2f}s", flush=True)
    
    norms_to_add = []
    norms_to_update_dicts = []
    
    for row_idx, row in enumerate(rows):
        loan_id = row.get("loan_id", "").strip()
        raw_record = raw_records[row_idx]
        
        try:
            changes = {"batch_id": batch.id, "raw_record_id": raw_record.id}
            
            if source_type == "loan_tape":
                changes["borrower_id"] = row.get("borrower_id")
                changes["loan_type"] = row.get("loan_type")
                changes["origination_date"] = parse_date(row.get("origination_date"))
                changes["maturity_date"] = parse_date(row.get("maturity_date"))
                changes["original_principal"] = parse_float(row.get("original_principal"))
                changes["current_balance"] = parse_float(row.get("current_balance"))
                changes["interest_rate"] = parse_float(row.get("interest_rate"))
                changes["term_months"] = parse_int(row.get("term_months"))
                changes["borrower_state"] = row.get("borrower_state")
                changes["loan_purpose"] = row.get("loan_purpose")
                changes["credit_grade"] = row.get("credit_grade")
                changes["employment_length"] = row.get("employment_length")
                changes["income_band"] = row.get("income_band")
                changes["payment_status"] = row.get("payment_status")
                changes["days_past_due"] = parse_int(row.get("days_past_due"))
                changes["servicer_name"] = row.get("servicer_name")
                changes["last_payment_date"] = parse_date(row.get("last_payment_date"))
                changes["last_updated_at"] = parse_date(row.get("last_updated_at"))
                changes["document_status"] = row.get("document_status")
                changes["source_system"] = row.get("source_system")

            elif source_type == "servicer_update":
                changes["servicer_update_current_balance"] = parse_float(row.get("current_balance"))
                changes["servicer_update_interest_rate"] = parse_float(row.get("interest_rate"))
                changes["servicer_update_payment_status"] = row.get("payment_status")
                changes["servicer_update_days_past_due"] = parse_int(row.get("days_past_due"))
                changes["servicer_update_servicer_name"] = row.get("servicer_name")
                changes["servicer_update_last_payment_date"] = parse_date(row.get("last_payment_date"))
                changes["servicer_update_last_updated_at"] = parse_date(row.get("last_updated_at"))
                changes["servicer_update_document_status"] = row.get("document_status")

            elif source_type == "document_manifest":
                changes["manifest_document_status"] = row.get("document_status")
            
            if loan_id and loan_id in existing_norms:
                norm = existing_norms[loan_id]
                for k, v in changes.items():
                    setattr(norm, k, v)
            else:
                # Completely new record -> create ORM object for bulk insert
                norm = NormalizedLoan(loan_id=loan_id if loan_id else None, **changes)
                if loan_id:
                    existing_norms[loan_id] = norm
                norms_to_add.append(norm)
                
            normalized_count += 1
        except Exception as e:
            failed_count += 1

    print(f"[Timer] Processed rows in memory: {time.time() - start_t:.2f}s", flush=True)
    
    try:
        if norms_to_add:
            db.add_all(norms_to_add)
            
        print(f"[Timer] Starting final commit: {time.time() - start_t:.2f}s", flush=True)
        db.commit()
        print(f"[Timer] Finished final commit: {time.time() - start_t:.2f}s", flush=True)
    except Exception as e:
        db.rollback()
        failed_count += len(rows)
        normalized_count = 0
        
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
