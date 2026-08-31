import requests

base_url = "http://localhost:8000"
r = requests.post(f"{base_url}/api/auth/token", data={"username": "reviewer", "password": "demo123"}, timeout=5)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

try:
    r2 = requests.post(f"{base_url}/api/ai/generate-rule", headers=headers, json={"natural_language": "Test"}, timeout=5)
    print(f"Rule Gen: {r2.status_code} {r2.text}")
except Exception as e:
    print(f"Rule Gen failed: {e}")
