import requests
base_url = "http://127.0.0.1:8000"
r = requests.post(f"{base_url}/api/auth/token", data={"username": "operator", "password": "demo123"}, timeout=5)
print(r.status_code, r.text)
