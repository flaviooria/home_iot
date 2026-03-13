from fastapi import FastAPI

from v1.endpoints import api_router

app = FastAPI(title="Home IoT API")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema Home IoT"}


@app.get("/health")
async def health_check():
    return {"status": "online", "database": "connected"}
