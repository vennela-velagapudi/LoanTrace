import requests
base_url = "http://localhost:8000"
r = requests.post(f"{base_url}/api/auth/token", data={"username": "reviewer", "password": "demo123"}, timeout=5)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
r2 = requests.get(f"{base_url}/api/exceptions", headers=headers, timeout=5)
print(f"Exceptions: {r2.status_code}")
