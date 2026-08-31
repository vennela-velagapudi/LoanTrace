from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.api import auth, loans, exceptions, verified_loans, audit, summary, files, validation, ai
import traceback

from app.core.config import settings

app = FastAPI(title="LoanTrace API")

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import PlainTextResponse
import traceback

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            with open("middleware_error.txt", "w") as f:
                f.write(traceback.format_exc())
            return PlainTextResponse("Middleware caught exception", status_code=500)

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method in ["GET", "OPTIONS"]:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(ExceptionLoggingMiddleware)
app.add_middleware(NoCacheMiddleware)

origins = [origin.strip() for origin in settings.FRONTEND_URL.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(loans.router, prefix="/api/loans", tags=["loans"])
app.include_router(exceptions.router, prefix="/api/exceptions", tags=["exceptions"])
app.include_router(verified_loans.router, prefix="/api/verified-loans", tags=["verified-loans"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(validation.router, prefix="/api/validation", tags=["validation"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": "disconnected"}
