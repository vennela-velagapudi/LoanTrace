from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/crash")
def crash():
    raise Exception("Boom")

if __name__ == "__main__":
    import uvicorn
    import threading
    import time
    import requests

    def run():
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(2)

    r = requests.post("http://127.0.0.1:8001/crash", headers={"Origin": "http://localhost:3000"})
    print(f"Status: {r.status_code}")
    print(f"Headers: {r.headers}")
