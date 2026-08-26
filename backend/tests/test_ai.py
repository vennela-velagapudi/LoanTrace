import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, ExceptionModel, NormalizedLoan, RawRecord, AIRecommendation, AuditLog
from app.core.security import get_current_user
import unittest.mock

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
    
    raw = RawRecord(id=1, row_index=1, row_data={"current_balance": 115000})
    db.add(raw)
    db.flush()
    
    loan = NormalizedLoan(
        id=1,
        loan_id="LOAN-123",
        current_balance=115000.0,
        original_principal=100000.0,
        raw_record_id=raw.id
    )
    db.add(loan)
    db.flush()
    
    exc = ExceptionModel(
        id=1,
        normalized_loan_id=loan.id,
        rule_name="balance_exceeds_principal",
        severity="HIGH",
        status="OPEN",
        description="Balance exceeds principal",
        version=1
    )
    db.add(exc)
    db.commit()
    yield

def get_reviewer():
    return User(id=1, username="test_reviewer", role="REVIEWER")

def get_unauthorized_user():
    return User(id=2, username="test_other", role="USER")

def test_explain_exception_rbac_unauthorized(db):
    app.dependency_overrides[get_current_user] = get_unauthorized_user
    res = client.post("/api/ai/exceptions/1/explain")
    assert res.status_code == 403

def test_explain_exception(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/exceptions/1/explain")
    assert res.status_code == 200
    data = res.json()
    assert "recommendation_id" in data
    assert "data" in data
    assert data["data"]["severity"] == "HIGH"
    assert "[Demo AI]" in data["data"]["explanation"]
    
    # Check persistence
    rec = db.query(AIRecommendation).first()
    assert rec is not None
    assert rec.action_type == "EXPLAIN"
    
    # Check audit log
    audit = db.query(AuditLog).filter(AuditLog.action == "AI_RECOMMENDATION_GENERATED").first()
    assert audit is not None

def test_suggest_correction(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/exceptions/1/suggest")
    assert res.status_code == 200
    data = res.json()
    assert "[Demo AI Suggestion]" in data["data"]["suggested_value"]
    
    # Original loan must NOT be modified
    loan = db.query(NormalizedLoan).first()
    assert loan.current_balance == 115000.0

def test_compare_conflict(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/exceptions/1/compare")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_value" in data["data"]
    
    rec = db.query(AIRecommendation).filter(AIRecommendation.action_type == "COMPARE").first()
    assert rec is not None

def test_batch_summary(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/batch-summary", json={"exception_ids": [1]})
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["total_exceptions_analyzed"] == 100

def test_generate_rule(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/generate-rule", json={"natural_language": "Flag if current balance > original principal"})
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["target_field"] == "current_balance"

def test_accept_recommendation(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    # First generate one
    res = client.post("/api/ai/exceptions/1/suggest")
    rec_id = res.json()["recommendation_id"]
    
    # Now accept it
    res = client.post(f"/api/ai/recommendations/{rec_id}/action", json={"action": "ACCEPT"})
    assert res.status_code == 200
    assert res.json()["status"] == "ACCEPTED"
    
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    assert rec.status == "ACCEPTED"
    
    audit = db.query(AuditLog).filter(AuditLog.action == "AI_RECOMMENDATION_ACCEPTED").first()
    assert audit is not None

def test_edit_recommendation(db):
    app.dependency_overrides[get_current_user] = get_reviewer
    res = client.post("/api/ai/exceptions/1/suggest")
    rec_id = res.json()["recommendation_id"]
    
    res = client.post(f"/api/ai/recommendations/{rec_id}/action", json={"action": "EDIT", "edited_value": "95000"})
    assert res.status_code == 200
    
    rec = db.query(AIRecommendation).filter(AIRecommendation.id == rec_id).first()
    assert rec.status == "EDITED"
    assert rec.structured_data["edited_value"] == "95000"
