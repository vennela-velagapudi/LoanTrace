import asyncio
from app.database import SessionLocal
from app.services.validation import run_validation

def test_val():
    db = SessionLocal()
    res = run_validation(db, batch_id=None)
    print(res)
    db.close()

if __name__ == "__main__":
    test_val()
