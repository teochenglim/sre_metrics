# fastapi_app.py
from fastapi import FastAPI, HTTPException
from sre_metrics import instrument_fastapi
import uvicorn

app = FastAPI()

# hard-coded metrics port
instrument_fastapi(
    app,
    metrics_port=9098,
    prefix="myapp_",
    group_status_codes=False
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/error")
def trigger_error():
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    # hard-coded app port
    uvicorn.run(app, host="0.0.0.0", port=8000)
