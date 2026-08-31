import requests
try:
    print("Sending /health request...")
    r = requests.get("http://127.0.0.1:8000/health")
    print(r.status_code, r.text)
except Exception as e:
    print(e)
