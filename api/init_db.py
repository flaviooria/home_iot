import asyncio
import sys

# --- ARREGLO PARA WINDOWS ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ----------------------------

from shared.database import engine, Base
from shared.models import Installation, Zone, Device, Telemetry  # type: ignore


async def init_db():
    async with engine.begin() as conn:
        print("🚀 Conectando a PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Estructura de 'home' creada correctamente.")
