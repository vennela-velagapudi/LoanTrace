from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Req(BaseModel):
    num: int

@app.post("/test")
def test(req: Req):
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    import threading
    import time
    import requests

    def run():
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(2)

    r = requests.post("http://127.0.0.1:8002/test", json={"num": "not_an_int"}, headers={"Origin": "http://localhost:3000"})
    print(f"Status: {r.status_code}")
    print(f"Headers: {r.headers}")
