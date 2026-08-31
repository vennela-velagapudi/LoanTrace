import requests
try:
    print("Sending /docs request...")
    r = requests.get("http://127.0.0.1:8000/docs", timeout=5)
    print(r.status_code)
except Exception as e:
    print(e)
