from app.database import SessionLocal
from app.models import ExceptionModel, UploadBatch, NormalizedLoan
from sqlalchemy import func

def run_diagnostics():
    db = SessionLocal()
    try:
        print("1. Total number of Exception records in the database:")
        total_exceptions = db.query(func.count(ExceptionModel.id)).scalar()
        print(f"Total: {total_exceptions}\n")

        print("2. Number of Exception records grouped by batch_id:")
        by_batch = db.query(NormalizedLoan.batch_id, func.count(ExceptionModel.id))\
                     .join(ExceptionModel, ExceptionModel.normalized_loan_id == NormalizedLoan.id)\
                     .group_by(NormalizedLoan.batch_id).all()
        for batch_id, count in by_batch:
            print(f"Batch {batch_id}: {count}")
        print("\n")

        print("3. Number of Exception records grouped by rule_name:")
        by_rule = db.query(ExceptionModel.rule_name, func.count(ExceptionModel.id)).group_by(ExceptionModel.rule_name).all()
        for rule, count in by_rule:
            print(f"Rule {rule}: {count}")
        print("\n")

        print("4. Number of Exception records grouped by status:")
        by_status = db.query(ExceptionModel.status, func.count(ExceptionModel.id)).group_by(ExceptionModel.status).all()
        for status, count in by_status:
            print(f"Status {status}: {count}")
        print("\n")

        print("5. Number of UploadBatch records:")
        batches = db.query(UploadBatch).order_by(UploadBatch.id).all()
        for b in batches:
            print(f"ID: {b.id}, Filename: {b.filename}, Type: {b.source_type}, Status: {b.status}, Uploaded: {b.uploaded_at}")
        print("\n")
        
        if batches:
            latest_batch = batches[-1]
            print(f"6. Exception count for the latest UploadBatch (ID {latest_batch.id}):")
            latest_count = db.query(func.count(ExceptionModel.id))\
                             .join(NormalizedLoan, ExceptionModel.normalized_loan_id == NormalizedLoan.id)\
                             .filter(NormalizedLoan.batch_id == latest_batch.id).scalar()
            print(f"Count: {latest_count}\n")

            print(f"7. Exceptions grouped by batch_id and rule_name for the latest batch (ID {latest_batch.id}):")
            by_latest_rule = db.query(ExceptionModel.rule_name, func.count(ExceptionModel.id))\
                               .join(NormalizedLoan, ExceptionModel.normalized_loan_id == NormalizedLoan.id)\
                               .filter(NormalizedLoan.batch_id == latest_batch.id)\
                               .group_by(ExceptionModel.rule_name).all()
            for rule, count in by_latest_rule:
                print(f"Rule {rule}: {count}")
            print("\n")
        else:
            print("No UploadBatch records found.\n")
    finally:
        db.close()

if __name__ == "__main__":
    run_diagnostics()
