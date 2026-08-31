import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.database import SessionLocal
from app.models import NormalizedLoan
from sqlalchemy.dialects.postgresql import insert

db = SessionLocal()
try:
    # Get one existing record
    norm = db.query(NormalizedLoan).first()
    if not norm:
        print("No records")
        sys.exit(0)
    
    print(f"Testing UPSERT on id={norm.id}")
    
    dicts = [
        {"id": norm.id, "loan_id": norm.loan_id, "current_balance": 9999.99}
    ]
    
    stmt = insert(NormalizedLoan)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={col.name: col for col in stmt.excluded if col.name != "id"}
    )
    
    db.execute(stmt, dicts)
    db.commit()
    print("Success!")
except Exception as e:
    print(e)
finally:
    db.close()
