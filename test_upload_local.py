import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.database import SessionLocal
from app.services.ingestion import ingest_csv
from app.services.validation import run_validation

db = SessionLocal()
try:
    with open("data/loan_tape.csv", "r", encoding="utf-8") as f:
        content = f.read()
    ingest_result = ingest_csv(db, content, "loan_tape.csv")
    print(ingest_result)
    valid_result = run_validation(db, ingest_result["batch_id"])
    print(valid_result)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
