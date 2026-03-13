from fastapi import FastAPI
from shared.database import engine
from shared.models import Base

app = FastAPI(title="Home IoT API")


@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema Home IoT"}


@app.get("/health")
async def health_check():
    return {"status": "online", "database": "connected"}
