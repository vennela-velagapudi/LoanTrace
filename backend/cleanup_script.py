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

def cleanup():
    db = SessionLocal()
    print("Starting cleanup analysis...")
    
    # 1. Identify latest completed batch
    latest_batch_id = db.execute(text("SELECT id FROM upload_batches WHERE status = 'COMPLETED' ORDER BY id DESC LIMIT 1")).scalar()
    if not latest_batch_id:
        print("No completed batch found.")
        return
        
    print(f"Latest completed batch: {latest_batch_id}")
    
    # 2. Identify latest validation run for this batch
    latest_run_id = db.execute(text(f"SELECT id FROM validation_runs WHERE batch_id = {latest_batch_id} ORDER BY id DESC LIMIT 1")).scalar()
    if not latest_run_id:
        print("No validation run found for latest batch.")
        return
        
    print(f"Latest validation run: {latest_run_id}")
    
    # We will delete all exceptions that do NOT belong to this latest run
    # To do this safely and respect FKs:
    # Get all validation_result_ids for the latest run
    # Delete AIRecommendations and ExceptionComments linked to exceptions NOT in that set
    # Delete Exceptions NOT in that set
    # Delete ValidationResults NOT in that set
    # Delete ValidationRuns != latest_run_id
    
    print("\n--- Dry Run / Plan ---")
    
    old_runs_count = db.execute(text(f"SELECT count(*) FROM validation_runs WHERE id != {latest_run_id}")).scalar()
    old_results_count = db.execute(text(f"SELECT count(*) FROM validation_results WHERE run_id != {latest_run_id}")).scalar()
    
    # Any exception whose validation_result_id is NOT in the latest run results (or is NULL)
    old_exceptions_count = db.execute(text(f"""
        SELECT count(*) FROM exceptions e 
        LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
        WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
    """)).scalar()
    
    old_comments_count = db.execute(text(f"""
        SELECT count(*) FROM exception_comments c
        JOIN exceptions e ON c.exception_id = e.id
        LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
        WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
    """)).scalar()
    
    old_ai_count = db.execute(text(f"""
        SELECT count(*) FROM ai_recommendations a
        JOIN exceptions e ON a.exception_id = e.id
        LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
        WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
    """)).scalar()
    
    print(f"To delete: {old_runs_count} old ValidationRuns")
    print(f"To delete: {old_results_count} old ValidationResults")
    print(f"To delete: {old_exceptions_count} old ExceptionModels")
    print(f"To delete: {old_comments_count} ExceptionComments")
    print(f"To delete: {old_ai_count} AIRecommendations")
    
    print("\nExecuting deletions...")
    
    # Execution
    db.execute(text(f"""
        DELETE FROM exception_comments 
        WHERE exception_id IN (
            SELECT e.id FROM exceptions e
            LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
            WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
        )
    """))
    
    db.execute(text(f"""
        DELETE FROM ai_recommendations 
        WHERE exception_id IN (
            SELECT e.id FROM exceptions e
            LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
            WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
        )
    """))
    
    db.execute(text(f"""
        DELETE FROM exceptions 
        WHERE id IN (
            SELECT e.id FROM exceptions e
            LEFT JOIN validation_results vr ON e.validation_result_id = vr.id
            WHERE e.validation_result_id IS NULL OR vr.run_id != {latest_run_id}
        )
    """))
    
    db.execute(text(f"DELETE FROM validation_results WHERE run_id != {latest_run_id}"))
    db.execute(text(f"DELETE FROM validation_runs WHERE id != {latest_run_id}"))
    
    db.commit()
    print("Cleanup successful.")
    
    # Verify
    rem_runs = db.execute(text("SELECT count(*) FROM validation_runs")).scalar()
    rem_exc = db.execute(text("SELECT count(*) FROM exceptions")).scalar()
    print(f"\nRemaining ValidationRuns: {rem_runs}")
    print(f"Remaining Exceptions: {rem_exc}")

if __name__ == "__main__":
    cleanup()
