from fastapi import FastAPI
from app.scheduler import run_scheduler

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Trading Platform is running"}

run_scheduler()
