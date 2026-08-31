import requests
import time

base_url = "http://127.0.0.1:8000"

file_path = "data/loan_tape.csv"
print(f"Uploading {file_path}...")

with open(file_path, "rb") as f:
    files = {"file": ("loan_tape.csv", f, "text/csv")}
    start = time.time()
    try:
        r2 = requests.post(f"{base_url}/api/files/upload", files=files, timeout=60)
        print(f"Upload Status: {r2.status_code}")
        print(f"Upload Result: {r2.text}")
    except Exception as e:
        print(f"Upload failed: {e}")
    print(f"Time taken: {time.time() - start:.2f} seconds")
