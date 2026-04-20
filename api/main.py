from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from v1.endpoints import api_router

app = FastAPI(title="Home IoT API")
app.include_router(api_router, prefix="/api/v1")

# origins = [
#     "http://localhost:3000",
# ] -- UNCOMMENT IF FRONTEND IN PRODUCTION

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema Home IoT"}


@app.get("/health")
async def health_check():
    return {"status": "online", "database": "connected"}
