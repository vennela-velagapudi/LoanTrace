import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, ExceptionModel, NormalizedLoan, RawRecord, VerifiedLoan, UploadBatch, ValidationRun, ValidationResult
from app.core.security import get_current_user
from app.core.hashing import generate_record_hash

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
    
    user_consumer = User(id=2, username="test_consumer", role="DATA_CONSUMER", hashed_password="fake")
    db.add(user_consumer)
    
    batch = UploadBatch(id=1, filename="test.csv", status="COMPLETED")
    db.add(batch)
    db.flush()
    
    val_run = ValidationRun(id=1, batch_id=batch.id)
    db.add(val_run)
    db.flush()

    raw = RawRecord(id=1, batch_id=batch.id, row_index=1, row_data={"current_balance": 100000})
    db.add(raw)
    db.flush()
    
    loan1 = NormalizedLoan(id=1, batch_id=batch.id, loan_id="L-1", current_balance=100000.0, raw_record_id=raw.id)
    loan2 = NormalizedLoan(id=2, batch_id=batch.id, loan_id="L-2", current_balance=50000.0, raw_record_id=raw.id)
    db.add(loan1)
    db.add(loan2)
    db.flush()
    
    val_res1 = ValidationResult(id=1, run_id=val_run.id, normalized_loan_id=loan1.id, is_valid=False)
    val_res2 = ValidationResult(id=2, run_id=val_run.id, normalized_loan_id=loan2.id, is_valid=False)
    db.add(val_res1)
    db.add(val_res2)
    db.flush()

    # Loan 1 has open exception
    exc = ExceptionModel(id=1, normalized_loan_id=loan1.id, validation_result_id=val_res1.id, rule_name="rule1", status="OPEN")
    # Loan 2 has resolved exception
    exc2 = ExceptionModel(id=2, normalized_loan_id=loan2.id, validation_result_id=val_res2.id, rule_name="rule2", status="RESOLVED", resolution_reason="Fixed")
    db.add(exc)
    db.add(exc2)
    db.commit()
    yield

def get_reviewer():
    return User(id=1, username="test_reviewer", role="REVIEWER")
    
def get_consumer():
    return User(id=2, username="test_consumer", role="DATA_CONSUMER")

def test_hashing_determinism():
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}
    assert generate_record_hash(data1) == generate_record_hash(data2)
    
    data3 = {"a": 1, "b": 3}
    assert generate_record_hash(data1) != generate_record_hash(data3)

def test_verification_blocked_by_exception(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/verified-loans/verify/L-1")
    assert res.status_code == 400
    assert "unresolved exceptions" in res.json()["detail"]

def test_verification_success(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/verified-loans/verify/L-2")
    assert res.status_code == 200
    
    v_id = res.json()["verified_loan_id"]
    rec = db.query(VerifiedLoan).filter(VerifiedLoan.id == v_id).first()
    assert rec.version == 1
    assert rec.record_hash == res.json()["hash"]
    
    # Check decisions included
    decisions = rec.verified_data["reviewer_decisions"]
    assert len(decisions) == 1
    assert decisions[0]["rule"] == "rule2"

def test_consumer_api_access(db):
    app.dependency_overrides[get_current_user] = get_consumer
    res = client.get("/api/verified-loans/")
    assert res.status_code == 200
    
def test_export_api_access(db):
    app.dependency_overrides[get_current_user] = get_consumer
    res = client.get("/api/verified-loans/export")
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/csv; charset=utf-8"

def test_dq_score(db):
    app.dependency_overrides[get_current_user] = get_consumer
    res = client.get("/api/summary/")
    assert res.status_code == 200
    data = res.json()
    assert data["total_loans"] == 2
    # L-1 has OPEN exception, so 1 out of 2 loans has open exception.
    # Score = 100 * (2 - 1) / 2 = 50.0
    assert data["data_quality_score"] == 50.0
