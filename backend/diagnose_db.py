import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def diagnose():
    db = SessionLocal()
    
    print("=== A. Upload Batches ===")
    batches = db.execute(text("SELECT id, filename, status, uploaded_at FROM upload_batches ORDER BY id DESC")).fetchall()
    print(f"Total batches: {len(batches)}")
    for b in batches:
        print(f"Batch {b.id}: {b.filename} - {b.status} - {b.uploaded_at}")
        
    print("\n=== B. Validation Runs ===")
    runs = db.execute(text("SELECT id, batch_id, run_time FROM validation_runs ORDER BY id DESC")).fetchall()
    print(f"Total runs: {len(runs)}")
    for r in runs:
        print(f"Run {r.id} for Batch {r.batch_id} at {r.run_time}")
        
    print("\n=== C. Exceptions ===")
    total_exc = db.execute(text("SELECT count(*) FROM exceptions")).scalar()
    print(f"Total Exceptions: {total_exc}")
    
    exc_by_run = db.execute(text("""
        SELECT vr.run_id, count(e.id) 
        FROM exceptions e
        LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
        GROUP BY vr.run_id
        ORDER BY vr.run_id DESC
    """)).fetchall()
    print("Exceptions by Validation Run:")
    for r in exc_by_run:
        print(f"Run {r.run_id}: {r[1]} exceptions")
        
    # Get latest completed batch
    latest_completed_batch = db.execute(text("SELECT id FROM upload_batches WHERE status = 'COMPLETED' ORDER BY id DESC LIMIT 1")).scalar()
    if latest_completed_batch:
        latest_run = db.execute(text(f"SELECT id FROM validation_runs WHERE batch_id = {latest_completed_batch} ORDER BY id DESC LIMIT 1")).scalar()
        if latest_run:
            exc_latest_run = db.execute(text(f"""
                SELECT count(e.id)
                FROM exceptions e
                JOIN validation_results vr ON e.validation_result_id = vr.id
                WHERE vr.run_id = {latest_run}
            """)).scalar()
            print(f"\nExceptions for latest run ({latest_run}): {exc_latest_run}")
            
            exc_by_status = db.execute(text(f"""
                SELECT e.status, count(e.id)
                FROM exceptions e
                JOIN validation_results vr ON e.validation_result_id = vr.id
                WHERE vr.run_id = {latest_run}
                GROUP BY e.status
            """)).fetchall()
            print("By Status:")
            for s in exc_by_status:
                print(f"  {s[0]}: {s[1]}")
                
            exc_by_rule = db.execute(text(f"""
                SELECT e.rule_name, count(e.id)
                FROM exceptions e
                JOIN validation_results vr ON e.validation_result_id = vr.id
                WHERE vr.run_id = {latest_run}
                GROUP BY e.rule_name
            """)).fetchall()
            print("By Rule Name:")
            for r in exc_by_rule:
                print(f"  {r[0]}: {r[1]}")
                
    # Check if there are exceptions without validation_result_id
    null_vr = db.execute(text("SELECT count(*) FROM exceptions WHERE validation_result_id IS NULL")).scalar()
    print(f"\nExceptions with NULL validation_result_id: {null_vr}")

if __name__ == "__main__":
    diagnose()
