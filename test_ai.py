import sys
import os
import requests

sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.database import SessionLocal
from app.models import User, ExceptionModel

db = SessionLocal()
# find a reviewer
rev = db.query(User).filter(User.role == "REVIEWER").first()
# find EXC-3
exc = db.query(ExceptionModel).filter(ExceptionModel.id == 3).first()
if not rev or not exc:
    print("Missing data")
    sys.exit(1)

# we need a token for the user
import requests

API_URL = "http://localhost:8000"
# Login
data = {"username": rev.username, "password": "demo123"}
r = requests.post(f"{API_URL}/api/auth/token", data=data)
if not r.ok:
    print(f"Login failed: {r.text}")
    sys.exit(1)
token = r.json()["access_token"]

# Test batch summary
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"exception_ids": [3]}
r2 = requests.post(f"{API_URL}/api/ai/batch-summary", headers=headers, json=payload)
print(f"Batch Summary Status: {r2.status_code}")
print(f"Batch Summary Response: {r2.text}")

# Test rule generator
payload2 = {"natural_language": "Flag loans where the current balance is greater than zero even though the loan status is closed."}
r3 = requests.post(f"{API_URL}/api/ai/generate-rule", headers=headers, json=payload2)
print(f"Generate Rule Status: {r3.status_code}")
print(f"Generate Rule Response: {r3.text}")
