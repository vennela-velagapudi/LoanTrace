import requests
import json

base_url = "http://localhost:8000"

print("1. Testing /health")
try:
    r = requests.get(f"{base_url}/health", timeout=5)
    print(f"Health: {r.status_code} {r.text}")
except Exception as e:
    print(f"Health failed: {e}")

print("2. Getting token")
token = None
try:
    r = requests.post(f"{base_url}/api/auth/token", data={"username": "reviewer", "password": "demo123"}, timeout=5)
    print(f"Login: {r.status_code}")
    if r.ok:
        token = r.json()["access_token"]
except Exception as e:
    print(f"Login failed: {e}")

if token:
    print("3. Testing /api/ai/batch-summary")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r2 = requests.post(f"{base_url}/api/ai/batch-summary", headers=headers, json={"exception_ids": [3]}, timeout=5)
        print(f"Batch Summary: {r2.status_code} {r2.text}")
    except Exception as e:
        print(f"Batch Summary failed: {type(e).__name__}: {e}")
        
    print("4. Testing OPTIONS /api/ai/batch-summary for CORS")
    try:
        r3 = requests.options(f"{base_url}/api/ai/batch-summary", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
        print(f"OPTIONS status: {r3.status_code}")
        print(f"OPTIONS headers: {r3.headers}")
    except Exception as e:
        print(f"OPTIONS failed: {e}")
