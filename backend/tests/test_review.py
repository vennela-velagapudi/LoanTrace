import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, ExceptionModel, NormalizedLoan, AuditLog, ExceptionComment, RawRecord, UploadBatch, ValidationRun, ValidationResult
from app.core.security import get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    db.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db(db):
    user_reviewer = User(id=1, username="test_reviewer", role="REVIEWER", hashed_password="fake")
    db.add(user_reviewer)
    
    user_other = User(id=2, username="test_other", role="USER", hashed_password="fake")
    db.add(user_other)
    
    batch = UploadBatch(id=1, filename="test.csv", status="COMPLETED")
    db.add(batch)
    db.flush()
    
    val_run = ValidationRun(id=1, batch_id=batch.id)
    db.add(val_run)
    db.flush()

    raw = RawRecord(id=1, batch_id=batch.id, row_index=1, row_data={"test": "data"})
    db.add(raw)
    db.flush()
    
    loan = NormalizedLoan(
        id=1,
        batch_id=batch.id,
        loan_id="LOAN-123",
        current_balance=100.0,
        interest_rate=0.05,
        payment_status="Current",
        days_past_due=0,
        servicer_name="Servicer A",
        document_status="Complete",
        borrower_state="CA",
        raw_record_id=raw.id
    )
    db.add(loan)
    db.flush()
    
    val_res = ValidationResult(id=1, run_id=val_run.id, normalized_loan_id=loan.id, is_valid=False)
    db.add(val_res)
    db.flush()

    exc = ExceptionModel(
        id=1,
        normalized_loan_id=loan.id,
        validation_result_id=val_res.id,
        rule_name="negative_balance",
        severity="HIGH",
        status="OPEN",
        description="Balance is negative",
        version=1
    )
    db.add(exc)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)

def get_reviewer():
    return User(id=1, username="test_reviewer", role="REVIEWER")

def get_unauthorized_user():
    return User(id=2, username="test_other", role="USER")

def test_get_exceptions():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.get("/api/exceptions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rule_name"] == "negative_balance"
    assert data[0]["status"] == "OPEN"

def test_get_exception_detail():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.get("/api/exceptions/1")
    assert response.status_code == 200
    data = response.json()
    assert data["exception"]["id"] == 1
    assert data["loan"]["loan_id"] == "LOAN-123"

def test_rbac_unauthorized():
    app.dependency_overrides[get_current_user] = get_unauthorized_user
    response = client.patch("/api/exceptions/1/assign", json={"user_id": 1})
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"

def test_assign_reviewer():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.patch("/api/exceptions/1/assign", json={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to"] == 1
    assert data["status"] == "IN_REVIEW"
    assert data["version"] == 2
    
    db = TestingSessionLocal()
    audit = db.query(AuditLog).filter(AuditLog.action == "REVIEWER_ASSIGNED").first()
    assert audit is not None
    assert audit.new_value["assigned_to"] == 1
    db.close()

def test_add_comment():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.post("/api/exceptions/1/comments", json={"text": "Looking into this"})
    assert response.status_code == 200
    data = response.json()
    assert data["comment_text"] == "Looking into this"
    
    db = TestingSessionLocal()
    comment = db.query(ExceptionComment).first()
    assert comment is not None
    assert comment.comment_text == "Looking into this"
    
    audit = db.query(AuditLog).filter(AuditLog.action == "REVIEW_COMMENT_ADDED").first()
    assert audit is not None
    db.close()

def test_edit_field():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.patch("/api/exceptions/1/fields", json={
        "field_name": "current_balance",
        "new_value": 200.0,
        "reason": "Fixing balance"
    })
    
    assert response.status_code == 200
    
    db = TestingSessionLocal()
    loan = db.query(NormalizedLoan).filter(NormalizedLoan.loan_id == "LOAN-123").first()
    assert loan.current_balance == 200.0
    
    audit = db.query(AuditLog).filter(AuditLog.action == "FIELD_EDITED").order_by(AuditLog.id.desc()).first()
    assert audit is not None
    assert audit.old_value["current_balance"] == 100.0
    assert audit.new_value["current_balance"] == 200.0
    
    exc = db.query(ExceptionModel).filter(ExceptionModel.id == 1).first()
    assert exc.status == "RESOLVED"
    
    db.close()

def test_decision_approve():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.post("/api/exceptions/1/decision", json={
        "decision": "APPROVE",
        "reason": "Looks good"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESOLVED"
    assert data["resolution_reason"] == "Looks good"
    assert data["version"] == 2
    
    db = TestingSessionLocal()
    audit = db.query(AuditLog).filter(AuditLog.action == "EXCEPTION_APPROVE").first()
    assert audit is not None
    db.close()

def test_decision_reject():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.post("/api/exceptions/1/decision", json={
        "decision": "REJECT",
        "reason": "Invalid"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"
    assert data["version"] == 2
    
    db = TestingSessionLocal()
    audit = db.query(AuditLog).filter(AuditLog.action == "EXCEPTION_REJECT").first()
    assert audit is not None
    db.close()

def test_decision_request_correction():
    app.dependency_overrides[get_current_user] = get_reviewer
    response = client.post("/api/exceptions/1/decision", json={
        "decision": "REQUEST_CORRECTION",
        "reason": "Needs fixing"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CORRECTION_REQUESTED"
    assert data["version"] == 2
    
    db = TestingSessionLocal()
    audit = db.query(AuditLog).filter(AuditLog.action == "EXCEPTION_REQUEST_CORRECTION").first()
    assert audit is not None
    db.close()

def test_concurrency_version_increment():
    app.dependency_overrides[get_current_user] = get_reviewer
    
    response = client.patch("/api/exceptions/1/assign", json={"user_id": 1})
    assert response.status_code == 200
    assert response.json()["version"] == 2
    
    response = client.post("/api/exceptions/1/decision", json={
        "decision": "APPROVE",
        "reason": "Approve it"
    })
    assert response.status_code == 200
    assert response.json()["version"] == 3
