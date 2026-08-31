import requests
import time

start = time.time()
try:
    r = requests.get("http://127.0.0.1:8000/health", timeout=30)
    print(r.status_code, r.text)
except Exception as e:
    print(e)
print(f"Time: {time.time() - start:.2f}s")
