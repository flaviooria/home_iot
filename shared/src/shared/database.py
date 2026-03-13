import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Cargamos el .env que está en la raíz del monorepo
load_dotenv()

# URL de conexión (usa el driver psycopg asíncrono)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/eter_db"
)

# Creamos el motor asíncrono
# echo=True mostrará todas las consultas SQL en la consola (útil para aprender)
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20)

# Fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Clase base para todos los modelos
class Base(DeclarativeBase):
    pass


# Dependencia para FastAPI (y otros servicios)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
