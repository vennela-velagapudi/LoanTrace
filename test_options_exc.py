import requests
base_url = "http://localhost:8000"
headers = {
    "Origin": "http://127.0.0.1:3000",
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "authorization"
}
try:
    r = requests.options(f"{base_url}/api/exceptions", headers=headers, timeout=5)
    print(f"OPTIONS status: {r.status_code}")
except Exception as e:
    print(f"OPTIONS failed: {e}")
