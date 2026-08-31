import requests
base_url = "http://localhost:8000"
headers = {
    "Origin": "http://127.0.0.1:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type"
}
try:
    r = requests.options(f"{base_url}/api/ai/batch-summary", headers=headers, timeout=5)
    print(f"OPTIONS status: {r.status_code}")
    print(f"OPTIONS headers: {r.headers}")
except Exception as e:
    print(f"OPTIONS failed: {e}")
