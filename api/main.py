from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from v1.endpoints import api_router

app = FastAPI(title="Home IoT API")
app.include_router(api_router, prefix="/api/v1")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las fuentes (ajustar según sea necesario)
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema Home IoT"}


@app.get("/health")
async def health_check():
    return {"status": "online", "database": "connected"}
