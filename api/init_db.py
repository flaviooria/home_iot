import asyncio
import sys

# --- ARREGLO PARA WINDOWS ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ----------------------------

from shared.database import engine, Base
from shared.models import Installation, Zone, Device  # type: ignore


async def init_db():
    async with engine.begin() as conn:
        print("🚀 Conectando a PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Estructura de 'home' creada correctamente.")


if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
