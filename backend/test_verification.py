import requests
import json
import time

API_URL = "http://127.0.0.1:8002"

# 1. Login
print("Logging in as operator...")
resp = requests.post(f"{API_URL}/api/auth/token", data={"username": "operator", "password": "demo123"})
if resp.status_code != 200:
    print("Login failed:", resp.text)
    exit(1)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful.")

# 2. Check empty summary
print("Checking summary BEFORE upload...")
resp = requests.get(f"{API_URL}/api/files/latest/summary", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print("BEFORE upload summary:", data)
    assert data is None, f"Expected None, got {data}"
else:
    print("Failed to get summary:", resp.text)
    exit(1)
print("Confirmed: Dashboard shows NO data (Empty Database).")

# 3. Upload file
print("Uploading data/loan_tape.csv...")
with open("../data/loan_tape.csv", "rb") as f:
    files = {"file": ("loan_tape.csv", f, "text/csv")}
    resp = requests.post(f"{API_URL}/api/files/upload", headers=headers, files=files)
if resp.status_code != 200:
    print("Upload failed:", resp.text)
    exit(1)
data = resp.json()
print("Upload successful:", data)

# 4. Check summary AFTER upload
print("Checking summary AFTER upload...")
resp = requests.get(f"{API_URL}/api/files/latest/summary", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print("AFTER upload summary:", data)
    assert data["total_rows"] == 2020, f"Expected 2020 total_rows, got {data['total_rows']}"
    assert data["normalized_count"] == 2020, f"Expected 2020 normalized_count, got {data['normalized_count']}"
    assert data["failed_count"] == 0, f"Expected 0 failed_count, got {data['failed_count']}"
    assert data["exceptions_created"] == 12464, f"Expected 12464 exceptions_created, got {data['exceptions_created']}"
else:
    print("Failed to get summary:", resp.text)
    exit(1)
print("Confirmed: All values match expected results AFTER upload!")
print("Clean-room verification PASSED!")
