import requests

base_url = "http://localhost:8000"

print("Testing OPTIONS /api/does-not-exist")
try:
    r3 = requests.options(f"{base_url}/api/does-not-exist", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    print(f"OPTIONS status: {r3.status_code}")
    print(f"OPTIONS headers: {r3.headers}")
except Exception as e:
    print(f"OPTIONS failed: {e}")
