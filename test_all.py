import requests

base_url = "http://127.0.0.1:8000"
headers = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}

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
    if r.ok:
        token = r.json()["access_token"]
except Exception as e:
    print(f"Login failed: {e}")

if token:
    headers["Authorization"] = f"Bearer {token}"
    print("3. Testing GET /api/exceptions")
    try:
        r2 = requests.get(f"{base_url}/api/exceptions", headers=headers, timeout=5)
        print(f"Exceptions: {r2.status_code}")
    except Exception as e:
        print(f"Exceptions failed: {e}")

    print("4. Testing POST /api/ai/batch-summary")
    try:
        r3 = requests.post(f"{base_url}/api/ai/batch-summary", headers=headers, json={"exception_ids": [3]}, timeout=5)
        print(f"Batch Summary: {r3.status_code}")
    except Exception as e:
        print(f"Batch Summary failed: {e}")
