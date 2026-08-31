import requests
import time

base_url = "http://127.0.0.1:8000"
headers = {"Origin": "http://127.0.0.1:3000"}

print("Getting token...")
r = requests.post(f"{base_url}/api/auth/token", data={"username": "operator", "password": "demo123"}, timeout=5)
token = r.json()["access_token"]
headers["Authorization"] = f"Bearer {token}"

file_path = "data/loan_tape.csv"
print(f"Uploading {file_path}...")

with open(file_path, "rb") as f:
    files = {"file": ("loan_tape.csv", f, "text/csv")}
    start = time.time()
    try:
        r2 = requests.post(f"{base_url}/api/files/upload", headers=headers, files=files)
        print(f"Upload Status: {r2.status_code}")
        print(f"Upload Result: {r2.text}")
    except Exception as e:
        print(f"Upload failed: {e}")
    print(f"Time taken: {time.time() - start:.2f} seconds")
