import requests
import json
import traceback

r = requests.post("http://127.0.0.1:8000/api/files/upload", files={"file": ("test.csv", "loan_id\n1", "text/csv")})
print(r.text)
