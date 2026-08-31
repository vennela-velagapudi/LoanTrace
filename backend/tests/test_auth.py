import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

# Use a separate memory engine for auth tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db_session
    yield db_session
    db_session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_login_success(db):
    res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(db):
    # First login to ensure seeds are created
    client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    
    res = client.post("/api/auth/token", data={"username": "reviewer", "password": "wrong"})
    assert res.status_code == 401

def test_consumer_blocked_from_reviewer_mutation(db):
    res = client.post("/api/auth/token", data={"username": "consumer", "password": "demo123"})
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    mutation_res = client.post("/api/exceptions/1/comments", json={"text": "test"}, headers=headers)
    assert mutation_res.status_code == 403

def test_operator_blocked_from_reviewer_mutation(db):
    res = client.post("/api/auth/token", data={"username": "operator", "password": "demo123"})
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    mutation_res = client.post("/api/exceptions/1/comments", json={"text": "test"}, headers=headers)
    assert mutation_res.status_code == 403

def test_reviewer_allowed_reviewer_mutation(db):
    res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    mutation_res = client.post("/api/exceptions/1/comments", json={"text": "test"}, headers=headers)
    # 404 means it passed RBAC and failed to find exception ID 1, which is correct since we didn't mock exception 1 here
    assert mutation_res.status_code == 404

def test_change_password_success(db):
    res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    change_res = client.post("/api/auth/change-password", json={"current_password": "demo123", "new_password": "newpassword123"}, headers=headers)
    assert change_res.status_code == 200
    
    # Old password should fail
    fail_res = client.post("/api/auth/token", data={"username": "reviewer", "password": "demo123"})
    assert fail_res.status_code == 401
    
    # New password should succeed
    success_res = client.post("/api/auth/token", data={"username": "reviewer", "password": "newpassword123"})
    assert success_res.status_code == 200

def test_change_password_wrong_current(db):
    res = client.post("/api/auth/token", data={"username": "operator", "password": "demo123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    change_res = client.post("/api/auth/change-password", json={"current_password": "wrongpassword", "new_password": "newpassword123"}, headers=headers)
    assert change_res.status_code == 400
    assert change_res.json()["detail"] == "Incorrect current password"
