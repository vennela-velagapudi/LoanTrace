import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.database import SessionLocal
from app.models import ExceptionModel

db = SessionLocal()
exc = db.query(ExceptionModel).filter(ExceptionModel.id == 3).first()
if exc:
    print(f"EXC-3 actual_value: {repr(exc.actual_value)} type: {type(exc.actual_value)}")
    from app.api.ai import build_exception_context
    ctx = build_exception_context(exc)
    print("Context built.")
    import json
    try:
        json.dumps(ctx)
        print("JSON dumps successful.")
    except Exception as e:
        print("JSON dumps failed:", e)
else:
    print("EXC-3 not found.")
