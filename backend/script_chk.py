from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ExceptionModel

db = SessionLocal()
excs = db.query(ExceptionModel).all()
print(f"Total exceptions: {len(excs)}")
for e in excs[:5]:
    print(f"ID: {e.id}, Status: {e.status}")
