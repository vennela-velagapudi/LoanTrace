from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.api import auth, loans, exceptions, verified_loans, audit, summary, files, validation, ai

app = FastAPI(title="LoanTrace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(exceptions.router, prefix="/exceptions", tags=["exceptions"])
app.include_router(verified_loans.router, prefix="/verified-loans", tags=["verified-loans"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(validation.router, prefix="/validation", tags=["validation"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": "disconnected"}
